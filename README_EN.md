# Network Tools

This is a Flask-based web application that provides professional network management and development tools, including MIB file parser and SNMP OID calculator.

## 🛠️ Development Tools

This project is built with the following modern development toolchain:

- **IDE**: Visual Studio Code
- **AI Assistant**: Cline (VSCode Extension)
- **AI Model**: GLM-4.6 (Zhipu AI)
- **Development Method**: AI-assisted development with human optimization

## 🌟 Features

### 🌐 Internationalization Support
- 🌍 **Multi-language Support**: Chinese and English interface switching
- 🔄 **Real-time Switching**: Support for URL parameter and link switching
- 💾 **Session Memory**: Language preferences automatically saved
- 🎯 **Smart Detection**: Automatic language selection based on browser language on first visit
- 📱 **Full Site Support**: All pages and features support multiple languages

### 🌳 MIB File Parser
- 📁 Drag-and-drop MIB file upload support
- 🌳 **Clickable Tree Structure**: Display MIB objects in an interactive tree view
- 🏗️ **Correct Parent-Child Relationships**: Hierarchical structure organization
- 📊 Parse OBJECT-TYPE, OBJECT IDENTIFIER, MODULE-IDENTITY, etc.
- 🔍 Display syntax, access permissions, status, and other detailed information
- 🔢 **Numeric OID Display**: Automatically calculate and display complete numeric OIDs (e.g., 1.3.6.1.4.1.99999.1.1.1)
- ✨ Smooth expand/collapse animations
- 🎨 Modern web interface
- 📱 Responsive design

### 🧮 SNMP Command Generator
- 🎯 Support for MIB Table (snmpwalk) and leaf node (snmpget) queries
- 🔐 Complete SNMPv1/v2c/v3 support
- ⚙️ Intelligent parameter configuration and validation
- 📋 One-click copy generated commands
- 🎨 Intuitive user interface
- 📝 Detailed usage examples and help text

### 🔢 MIB OID Generator
- 🎯 Intelligent OID path calculation and generation
- 🌳 Support for automatic OID structure extraction from MIB files
- 📊 Real-time display of complete numeric OID paths
- 🔍 Support for OID format validation and error correction
- 📋 One-click copy generated OIDs
- 🎨 Modern user interface design
- 📱 Fully responsive layout
- ✨ Support for batch OID generation and export

### 🏠 Unified Navigation Interface
- 🎨 Modern tool collection display page
- 🔄 Smooth page navigation experience
- 📱 Fully responsive design
- ✨ Elegant animation effects

## 🆕 Latest Improvements

### 1. Clickable Tree Nodes
- ✅ Fixed node click expand/collapse functionality
- ✅ Entire node items are clickable
- ✅ Added smooth expand/collapse animations
- ✅ Arrow icons show current state (▶/▼)

### 2. Correct Parent-Child Hierarchical Structure
- ✅ Redesigned MIB parsing logic
- ✅ Automatically build parent-child relationships based on OID paths
- ✅ Implemented true tree hierarchical structure instead of flat display
- ✅ Intelligent object organization and grouping

### 3. Numeric OID Calculation and Display
- ✅ Automatically calculate complete numeric OID paths
- ✅ Support standard SNMP OID root nodes (e.g., enterprises = 1.3.6.1.4.1)
- ✅ Green highlight display for easy identification and copying
- ✅ Display simultaneously with symbolic OIDs for easy comparison

## Installation and Running

### 1. Clone Project
```bash
git clone <your-repo-url>
cd flask_web
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# Or on Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
cd src && python app.py
```

The application will start at http://localhost:5000

## Usage

### 1. Access Application
- Open browser and visit `http://localhost:5000`
- Will display the network tools collection navigation page

### 2. Use MIB File Parser
- Click "MIB File Parser" on the navigation page
- Click upload area to select files, or directly drag files to the upload area
- Supported file formats: `.mib`, `.txt`, `.my`
- Files will automatically start parsing after upload

### 3. Use SNMP Command Generator
- Click "SNMP Command Generator" on the navigation page
- Select query type (MIB Table or leaf node)
- Enter OID or MIB name
- Configure SNMP parameters (version, community, etc.)
- Click "Generate Command" to get executable SNMP commands

### 4. Use MIB OID Generator
- Click "MIB OID Generator" on the navigation page
- Upload MIB files or enter OID paths
- System will automatically parse and generate complete numeric OIDs
- Support for batch generation and format validation
- One-click copy generated OID results

### 5. Language Switching
- **URL Parameter Switching**: Direct access `http://localhost:5000/?lang=en` (English) or `http://localhost:5000/?lang=zh` (Chinese)
- **Page Link Switching**: Click "Chinese"/"English" link in the top right corner of the page
- **Automatic Language Detection**: Automatically select interface language based on browser language on first visit
- **Session Memory**: Language preferences will be maintained throughout the entire session without repeated settings

### 6. View MIB Parsing Results
- After parsing is complete, will display **hierarchical** tree structure
- **Click any node** to expand/collapse child items (not just the arrow)
- Each node displays name, type, OID, and detailed information
- **Automatic organization** of parent-child relationships and display of numeric OIDs, such as:
  ```
  📦 Module: sampleMIB
  └── 🏷️ sampleObjects { sampleMIB 1 } [1.3.6.1.4.1.99999.1]
      ├── 🏷️ sampleSystemInfo { sampleObjects 1 } [1.3.6.1.4.1.99999.1.1]
      │   ├── 🔧 sampleSystemName { sampleSystemInfo 1 } [1.3.6.1.4.1.99999.1.1.1]
      │   └── 🔧 sampleSystemVersion { sampleSystemInfo 2 } [1.3.6.1.4.1.99999.1.1.2]
      └── 🔧 sampleConfigTable { sampleObjects 2 } [1.3.6.1.4.1.99999.1.2]
          └── 🔧 sampleConfigEntry { sampleConfigTable 1 } [1.3.6.1.4.1.99999.1.2.1]
  ```

## Supported MIB Elements

- **MODULE-IDENTITY**: MIB module definition
- **OBJECT-TYPE**: MIB object definition
- **OBJECT IDENTIFIER**: Object identifier
- **SYNTAX**: Object syntax type
- **MAX-ACCESS**: Access permissions
- **STATUS**: Object status

## Example Files

The project includes an example MIB file `sample_mibs/SAMPLE-MIB.mib` which you can use to test parsing functionality.

## Testing

Run test scripts:
```bash
python test_mib_parser.py
```

## Project Structure

```
flask_web/
├── src/                    # Source code directory
│   ├── app.py             # Main application file
│   ├── config.py          # Configuration file
│   ├── routes.py          # Routing module
│   ├── file_handler.py    # File handling module
│   ├── mib_parser.py     # MIB parsing module
│   └── i18n/             # Internationalization module
│       └── __init__.py   # Babel internationalization configuration
├── locales/               # Translation files directory
│   ├── zh/               # Chinese translations
│   │   └── LC_MESSAGES/
│   │       ├── messages.po # Translation source file
│   │       └── messages.mo # Compiled translation file
│   └── en/               # English translations
│       └── LC_MESSAGES/
│           ├── messages.po # Translation source file
│           └── messages.mo # Compiled translation file
├── tests/                 # Test files
│   ├── test_mib_parser.py # MIB parser test
│   ├── test_multi_mib.py  # Multi-file upload test
│   └── test_zip_upload.py # ZIP file upload test
├── test_data/            # Test data
│   ├── sample_mibs/      # Example MIB files
│   └── test_mibs.zip    # Test ZIP package
├── examples/             # Examples
│   └── browser_test.html # Browser test page
├── templates/            # Template files
│   ├── index.html        # Network tools navigation page (homepage)
│   ├── mib_parser.html   # MIB parser page
│   ├── oid_calculator.html # SNMP command generator page
│   └── mib_oid_generator.html # MIB OID generator page
├── uploads/              # Upload file directory
├── requirements.txt       # Python dependencies
├── babel.cfg            # Babel configuration file
├── README.md             # Project documentation (Chinese)
├── README_EN.md          # Project documentation (English)
├── DEPLOYMENT.md         # Deployment instructions
└── venv/                 # Python virtual environment
```

## API Interface

### POST /upload-mib
Upload and parse MIB files

**Request Parameters:**
- `mib_file`: Uploaded MIB file

**Response Format:**
```json
{
  "success": true,
  "module": "module_name",
  "tree": [
    {
      "text": "object_name",
      "type": "object|identifier|module",
      "oid": "OID_value",
      "syntax": "syntax_type",
      "children": []
    }
  ]
}
```

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Internationalization**: Flask-Babel (supports multi-language switching)
- **MIB Parsing**: Custom parser (based on regular expressions)
- **UI Framework**: Native CSS + JavaScript

## Contributing

Welcome to submit issues and pull requests to improve this project.

## 🚀 Deployment Guide

### Quick Deployment

This project supports multiple production environment deployment methods. For detailed configuration, please refer to [DEPLOYMENT.md](DEPLOYMENT.md) and [deployment/README.md](deployment/README.md)

#### 1. Docker Deployment (Recommended)
```bash
# Clone project
git clone git@github.com:leezii/SimpleMIBTree.git
cd SimpleMIBTree

# One-click Docker deployment
cd deployment/docker
chmod +x deploy.sh
./deploy.sh
```

#### 2. Heroku Cloud Deployment
```bash
# After installing Heroku CLI
cd deployment/heroku
chmod +x deploy.sh
./deploy.sh
```

#### 3. Systemd Service Deployment
```bash
# Suitable for Linux servers
cd deployment/systemd
chmod +x deploy.sh
# Modify APP_PATH variable in deploy.sh
./deploy.sh
```

#### 4. Traditional Nginx + Gunicorn Deployment
```bash
# Manual configuration
pip install gunicorn
# Copy configuration files and modify paths
sudo cp deployment/nginx/flask-web /etc/nginx/sites-available/
sudo cp deployment/systemd/flask-web.service /etc/systemd/system/
sudo cp deployment/systemd/gunicorn.conf.py /path/to/app/
# Start services
sudo systemctl start flask-web
sudo systemctl restart nginx
```

### Production Environment Access

After deployment is complete, the application will be accessible through:
- **Docker**: http://localhost (port 80)
- **Heroku**: https://your-app-name.herokuapp.com
- **Systemd**: http://your-domain.com
- **Nginx**: http://your-domain.com

### Environment Requirements

- **Python**: 3.8+
- **Memory**: Minimum 512MB
- **Storage**: Minimum 1GB
- **System**: Linux/Ubuntu/CentOS (recommended)

## License

MIT License
