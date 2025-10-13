# 🧠 Security Event Encyclopedia

[![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)](#)
[![Security](https://img.shields.io/badge/Security-Hardened-orange.svg)](#-security-highlights)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

The **Security Event Encyclopedia** is a secure, desktop-based cybersecurity tool that centralizes event IDs, descriptions, and response guidance from multiple platforms. It helps SOC analysts and security engineers investigate incidents faster with MITRE mapping, encrypted notes, safe imports, validated URLs, and robust data protection.

---

## 🚀 Key Features

- 🔎 **Centralized Event Knowledge Base** — Access details for Windows, Sysmon, SharePoint, SQL Server, Exchange, Linux, and Azure events.  
- 🧩 **MITRE ATT&CK Mapping** — Each event includes corresponding Tactics and Techniques for quick reference.  
- 🗝️ **Encrypted Analyst Notes** — Sensitive notes are stored securely to protect investigation data.  
- 🌐 **Safe URL Validation** — Prompts user confirmation before opening any external link.  
- 🧱 **Secure Import/Export** — Import events safely with file size checks; export to JSON or CSV.  
- 🏷️ **IOC Tagging & Advanced Search** — Tag, filter, and search events efficiently.  
- 🧾 **Custom Events Management** — Add, edit, and organize your own events with protection against modifying built-in ones.  

---

## 🛡️ Security Highlights

| Category | Finding | Risk Rating | Status |
|-----------|----------|-------------|--------|
| Web Link & External Calls | Insecure URL Handling | Medium | ✅ Mitigated with validation & confirmation |
| Database Security | Unencrypted Database | Medium | ✅ Notes encryption implemented |
| File Handling | Large File Imports | Low | ✅ File size checks added |
| Input Validation | Unrestricted Length | Low | ✅ Field length validation enforced |
| Injection Risks | SQL Injection | Very Low | ✅ Parameterized queries in use |

---

## 💾 Installation

### 1. Download
Go to the **[Releases](../../releases)** section of this repository and download the latest **SecurityEventEncyclopedia_Setup.exe** installer (COMING SOON).

### 2. Run the Installer
- Double-click the downloaded `.exe` file.  
- Follow the setup wizard created via *Advanced Installer*.  
- Choose your preferred installation directory.  

### 3. Launch the Application
After installation, the application will be available in your **Start Menu** or on your **Desktop** as a shortcut.

---

## 🧩 How to Use

1. **Search** for any Event ID or keyword.  
2. **View Details** — including severity, category, and MITRE mapping.  
3. **Add Custom Events** — extend the encyclopedia with your own data.  
4. **Add Secure Notes** — encrypt investigation notes for confidentiality.  
5. **Export Data** — share or archive your event records securely.

---

## 📊 Supported Platforms

- Windows Security Logs  
- Sysmon  
- SharePoint  
- SQL Server  
- Exchange  
- Linux Syslog  
- Azure / Cloud Events  

---

## 👨‍💻 Developer

Developed by **Rushab** — built for cybersecurity professionals, SOC analysts, and incident responders seeking a secure, all-in-one event reference companion.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE)) file for details.

---

## 📷 Application screenshots

<img width="1919" height="1026" alt="image" src="https://github.com/user-attachments/assets/2cc30a66-e5ac-4b59-a229-b2f7bb689f78" />
<img width="1919" height="1023" alt="image" src="https://github.com/user-attachments/assets/fafbecbe-29ef-44b4-891e-ea4862831948" />
<img width="1919" height="1031" alt="image" src="https://github.com/user-attachments/assets/3bd2e6cf-64aa-4d72-b37e-7b56724052ff" />
<img width="1916" height="1024" alt="image" src="https://github.com/user-attachments/assets/6000ea32-3d8e-41c3-880d-fc43737789d4" />
<img width="1917" height="1028" alt="image" src="https://github.com/user-attachments/assets/07c56492-80f2-4ae5-b70c-17844df9785a" />
