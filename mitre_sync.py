# mitre_sync.py
import requests
import json
import logging
import os
from datetime import datetime
from threading import Lock

# Set up logging
log_file = "mitre_sync_log.txt"
logger = logging.getLogger('MitreSync')
logger.setLevel(logging.INFO)
# Prevent duplicate handlers if module is reloaded
if not logger.hasHandlers():
    handler = logging.FileHandler(log_file, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class MitreSyncer:
    # URL for the MITRE ATT&CK Enterprise STIX data
    MITRE_STIX_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    
    def __init__(self, db, data_manager):
        self.db = db
        self.data_manager = data_manager
        self.tactic_map = {}
        self.technique_map = {}
        self.sync_lock = Lock()
        logger.info("MitreSyncer initialized.")

    def fetch_mitre_data(self):
        """
        Fetches the latest STIX data from the official MITRE CTI repository.
        """
        try:
            logger.info(f"Fetching MITRE data from {self.MITRE_STIX_URL}")
            response = requests.get(self.MITRE_STIX_URL, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes
            logger.info("Successfully fetched MITRE data.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch MITRE data: {e}")
            raise  # Re-raise to be caught by the sync thread

    def build_mappings(self, stix_data):
        """
        Parses the STIX bundle and builds simple lookup maps for tactics and techniques.
        """
        self.tactic_map = {}
        self.technique_map = {}

        if not stix_data.get('objects'):
            logger.error("STIX data is invalid or has no 'objects' key.")
            return

        logger.info("Building MITRE tactic and technique mappings...")
        
        # First pass: Get all tactics
        for obj in stix_data['objects']:
            if obj.get('type') == 'x-mitre-tactic' and obj.get('external_references'):
                tactic_id = obj['external_references'][0]['external_id']
                tactic_name = obj.get('name', 'Unknown Tactic')
                self.tactic_map[obj['id']] = {'name': tactic_name, 'id': tactic_id}

        # Second pass: Get all techniques and map them to tactics
        for obj in stix_data['objects']:
            if obj.get('type') == 'attack-pattern' and obj.get('external_references'):
                # Find the 'Txxxx' ID
                technique_id = None
                for ref in obj['external_references']:
                    if ref.get('source_name') == 'mitre-attack':
                        technique_id = ref['external_id']
                        break
                
                if not technique_id:
                    continue

                technique_name = obj.get('name', 'Unknown Technique')
                tactics = []
                
                if 'kill_chain_phases' in obj:
                    for phase in obj['kill_chain_phases']:
                        if phase.get('kill_chain_name') == 'mitre-attack':
                            # Look up the tactic name using its STIX ID
                            # We need to find the tactic object first
                            tactic_stix_id = self._find_tactic_stix_id(stix_data, phase.get('phase_name'))
                            if tactic_stix_id and tactic_stix_id in self.tactic_map:
                                tactics.append(self.tactic_map[tactic_stix_id]['id'])

                # Store by 'Txxxx' ID
                self.technique_map[technique_id] = {
                    'name': technique_name,
                    'tactics': sorted(list(set(tactics))) # Get unique, sorted tactic IDs
                }
        
        logger.info(f"Built mappings for {len(self.tactic_map)} tactics and {len(self.technique_map)} techniques.")

    def _find_tactic_stix_id(self, stix_data, phase_name):
        """Helper to find tactic STIX ID from phase_name (which is its short_name)."""
        for obj in stix_data['objects']:
             if obj.get('type') == 'x-mitre-tactic' and obj.get('x_mitre_shortname') == phase_name:
                 return obj.get('id')
        return None


    def run_sync(self, progress_callback=None, status_callback=None):
        """
        Main synchronization function.
        Fetches MITRE data, compares with local DB, and updates entries.
        """
        # Ensure only one sync runs at a time
        if not self.sync_lock.acquire(blocking=False):
            logger.warning("Sync already in progress.")
            if status_callback:
                status_callback("Sync is already running.")
            return

        try:
            if status_callback:
                status_callback("Fetching latest MITRE ATT&CK data...")
            
            stix_data = self.fetch_mitre_data()
            self.build_mappings(stix_data)
            
            if not self.technique_map:
                logger.error("Failed to build MITRE mappings. Aborting sync.")
                if status_callback:
                    status_callback("Error: Failed to build MITRE mappings. Check log.")
                return

            if status_callback:
                status_callback("Fetching all events from database...")
            
            all_events = self.db.search_events()
            total = len(all_events)
            updated_count = 0
            
            if status_callback:
                status_callback(f"Syncing {total} events...")

            for i, event in enumerate(all_events):
                # Extract the base 'Txxxx' or 'Txxxx.xxx' ID
                technique_id_full = event.get('mitre_technique', '')
                if not technique_id_full:
                    continue
                
                # Handle 'T1234 - Technique Name' format
                technique_id_base = technique_id_full.split(' ')[0]

                mitre_info = self.technique_map.get(technique_id_base)
                
                # Try parent technique if sub-technique not found (e.g., 'T1059.001' -> 'T1059')
                if not mitre_info and '.' in technique_id_base:
                     parent_id = technique_id_base.split('.')[0]
                     mitre_info = self.technique_map.get(parent_id)

                if mitre_info:
                    new_tactic_names = mitre_info['tactics']
                    new_tactic_str = " / ".join(new_tactic_names)
                    
                    # Get the full name for the ID we matched
                    matched_id = mitre_info.get('id', technique_id_base)
                    matched_name = mitre_info.get('name')

                    # Re-get the specific sub-technique name if we matched on parent
                    full_technique_str = f"{technique_id_base} - {self.technique_map.get(technique_id_base, {}).get('name', matched_name)}"


                    # Check if an update is needed
                    if event.get('mitre_tactic') != new_tactic_str or event.get('mitre_technique') != full_technique_str:
                        # Create a full event_data dict for the update
                        event_data = {
                            "event_id": event["event_id"],
                            "platform": event["platform"],
                            "event_title": event["event_title"],
                            "description": event.get("description", ""),
                            "severity": event.get("severity", "Unknown"),
                            "category": event.get("category", ""),
                            "response_guidance": event.get("response_guidance", ""),
                            "reference_links": event.get("reference_links", []),
                            "mitre_tactic": new_tactic_str,
                            "mitre_technique": full_technique_str,
                            "tags": event.get("tags", ""),
                        }
                        
                        if self.db.add_event(event_data): # add_event handles updates
                            logger.info(f"Updated Event ID {event['event_id']} ({event['platform']}): Tactic='{new_tactic_str}', Technique='{full_technique_str}'")
                            updated_count += 1
                        else:
                            logger.error(f"Failed to update Event ID {event['event_id']} in database.")

                if progress_callback:
                    progress_callback((i + 1) / total)
            
            logger.info(f"Sync complete. {updated_count} events updated.")
            if status_callback:
                status_callback(f"Sync complete. {updated_count} events updated.")
            
            # Finally, save changes to custom_events.json
            if updated_count > 0:
                if status_callback:
                    status_callback("Saving updates to custom_events.json...")
                self.data_manager.save_custom_events()
                logger.info("Saved updated custom events to JSON.")

            if status_callback:
                status_callback("MITRE ATT&CK Sync Finished.")

        except Exception as e:
            logger.error(f"An error occurred during sync: {e}", exc_info=True)
            if status_callback:
                status_callback(f"Error during sync: {e}. Check log for details.")
        finally:
            self.sync_lock.release()