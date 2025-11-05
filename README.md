
# 🛰️ SATELEYE // ORBITAL SURVEILLANCE NODE

- **Version:** 1.0
- **Author:** [Zer0plusOne](https://github.com/Zer0plusOne)
- **Date:** November 2025
- **Stack:** Python (Flask) · JavaScript (Leaflet) · HTML5/CSS3
- **Status:** Stable Release

---
## 🧩 Overview

**SATELEYE** is a local web-based orbital surveillance platform designed with a **governmental / NORAD-like interface**.

It provides real-time visualization of active satellites over a chosen location, combining the **UCS Satellite Database** and the **N2YO API** into a cohesive tactical dashboard.

The application is fully autonomous, running locally via Flask and using a modern, military-style dark interface rendered with Leaflet.

---
## ⚙️ System Architecture


```python
SATELEYE/
│
├── app.py # Flask backend: API bridge + logic
├── config.json # User configuration (location, API key)
├── usage.json # Local request counter and reset timer
│
├── static/
│ ├── script.js # Client-side logic (map, radar, logs)
│ ├── style.css # NORAD-style interface theme
│ └── assets/ # Fonts, icons, or visual resources
│
└── templates/
└── index.html # Main front-end layout

```

**Languages & Frameworks**

- Python 3.11 + Flask + Pandas + Requests
- HTML5 / CSS3 / JavaScript (Leaflet 1.9.4)
- UI Font: `Share Tech Mono`

---
## 🧠 Functional Workflow

1.  **Boot Sequence**

	1.1 A simulated authentication console runs before the interface loads.

	1.2 It mimics a NORAD-style terminal sequence before initializing the map.


2.  **UCS Database Auto-Fetch**

	The app automatically downloads the latest *UCS Satellite Database* (Excel → CSV conversion).


3.  **Satellite Retrieval**

	Real-time data is fetched from the **N2YO API**, filtered by coordinates defined in `config.json`.


4.  **Cross-Referencing**

	Each detected satellite is matched with the UCS dataset to display:


	- Country of Operator
	- Purpose / Type
	- Users / Organization


5.  **Visualization**

	- Live dark-mode map (`CartoDB Dark Matter` tiles)
	- Radar pulse at observer coordinates
	- Satellite markers with interactive popups
	- Expandable side panel for detailed data

---
## 🌍 Configuration (`config.json`)

  
```json
{

	"n2yo_api_key": "YOUR_API_KEY_HERE", // get yours free at https://www.n2yo.com/api/

	"latitude": -3.647461, // use your live location, thats Madrid location, read commment below.

	"longitude": 40.346544,

	"altitude": 667

}

// Can use https://epsg.io/map#srs=4326&x=-3.581543&y=40.430224&z=6&layer=streets to pick yours
```
 

| Field | Description |
|-------|--------------|
| `n2yo_api_key` | Personal key from [N2YO API](https://www.n2yo.com/api/). |
| `latitude` / `longitude` | Observer coordinates. |
| `altitude` | Altitude in meters. |

---
## 🧩 Main Components

### `app.py`

	- Core Flask backend.
	- Handles `/api/satellites` and `/api/update_ucs`.
	- Manages UCS database download + conversion.
	- Performs API requests to N2YO.
	- Implements monthly usage tracking.

### `index.html`

	- Structural layout of the application:
	- Top header with system indicators.
	- Left control/log panel.
	- Main satellite map section.
	- Classified footer label.

### `style.css`

	- Thematic design: **dark military console / NSA-like aesthetic**
	- Colors: black background, teal/cyan accents.
	- Animated radar pulse and boot sequence.
	- Responsive layout for both desktop and widescreen setups.

### `script.js`

	- Front-end behavior controller.
	- Boot terminal animation.
	- Leaflet initialization with dark tiles.
	- Radar + coverage circle.
	- Data synchronization and event logging.
	- Manual refresh and dynamic satellite list.

---
## 🛰️ Example Run

```powershell

> python app.py

✅  UCS  Database  detected (7560 records)
🌐  Server  started  on  http://localhost:1610
[20:00:01] Initializing SATELEYE Node...
[20:00:07] Map initialized successfully.
[20:00:08] Data synchronized (98  satellites).

```

---
## 🔐 Security & Privacy

- 100% local — no credentials or location data are sent externally.

- External endpoints used:

	-  `https://api.n2yo.com` for real-time satellite positions.
	-  `https://www.ucsusa.org` for official UCS database downloads.

- Logs and usage data remain on disk in local JSON files.

---
## 🧮 API Usage Limits

| Type | Monthly Free Limit |
|------:|------------------:|
| `verb_limit` | 1000 |
| `positions` | 1000 |
| `visualpasses` | 100 |
| `radiopasses` | 100 |
| `above` | 100 |

---
## 📦 Installation & Execution

  
```bash
git  clone  https://github.com/Zer0plusOne/SATELEYE.git
cd  SATELEYE
pip  install  -r  requirements.txt
python  app.py
```

Then open your browser and navigate to:

```r
http://localhost:1610
```

---
## 🧾 Licensing & Credits

-  **Author:** Zer0plusOne (Guillermo Gómez Sánchez)

-  **Frameworks:** Flask, Leaflet, Pandas

-  **Data Sources:**

	- UCS Satellite Database © Union of Concerned Scientists
	- N2YO API © N2YO.com
	- Map tiles © OpenStreetMap & CartoDB
	-  **License:** MIT — free for educational and research purposes.

---
## 🚀 Future Roadmap

| Version | Planned Features                                                                                          |
| ------- | --------------------------------------------------------------------------------------------------------- |
| **1.1** | Visual alerting for classified or military satellites, satellite export (CSV/PDF), minor UI enhancements. |
| **2.0** | Multi-observer tracking, user authentication, live orbital trajectory visualization.                      |
| **2.5** | Integration with NASA’s public data APIs and custom 3D orbital viewer.                                    |

---
## 🧭 Version History

| Version  |    Date    |                                     Key Changes                                     |
| :------: | :--------: | :---------------------------------------------------------------------------------: |
| **1.0**  | 2025-11-05 | First stable release: UCS auto-update, N2YO integration, dark map, radar interface. |
| 0.9-beta | 2025-11-03 |              Functional prototype with live data and basic interface.               |
| 0.7-dev  | 2025-11-01 |                     Core API bridge and satellite data parsing.                     |

---
## 🪪 Attribution

> *"Confidential Orbital Intelligence Interface // Developed by Zer0plusOne"*

> Built for research, cybersecurity, and open-source education.

> *Bellum omnium contra omnes.*
