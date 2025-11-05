// === SATELEYE 3.2 ===


let map, markerGroup, radarMarker, coverageCircle;
const logArea = document.getElementById("ucs-log");


function logMessage(msg, type = "info") {
  const timestamp = new Date().toLocaleTimeString("en-GB", { hour12: false });
  const p = document.createElement("p");
  p.textContent = `[${timestamp}] ${msg}`;
  p.classList.add(type);
  logArea.prepend(p);
  if (logArea.children.length > 60) logArea.removeChild(logArea.lastChild);
}


async function bootSequence() {
  const lines = [
    "> INITIALIZING SATELEYE NODE 03...",
    "> AUTHORIZATION: VERIFIED",
    "> ESTABLISHING SECURE LINK TO NORAD...",
    "> SYNCING ORBITAL DATABASE...",
    "> SYSTEM ONLINE",
  ];
  const bootLog = document.getElementById("boot-log");

  for (const line of lines) {
    bootLog.textContent += line + "\n";
    await new Promise(r => setTimeout(r, 700));
  }

  await new Promise(r => setTimeout(r, 800));
  const bootScreen = document.getElementById("boot-screen");
  bootScreen.classList.add("fade-out");


  setTimeout(async () => {
    bootScreen.style.display = "none";
    document.getElementById("main-header").style.display = "flex";
    document.getElementById("dashboard").style.display = "flex";
    document.getElementById("main-footer").style.display = "block";

    
    await initMap();
    await loadSatellites();

    
    setTimeout(() => {
      if (map) map.invalidateSize();
      logMessage("🛰️ Map refreshed after boot sequence.", "info");
    }, 500);
  }, 1500);
}


async function initMap() {
  try {
    const res = await fetch("/api/satellites?radius=1");
    const data = await res.json();
    const lat = data.satellites?.[0]?.lat ?? 40.4168;
    const lng = data.satellites?.[0]?.lng ?? -3.7038;

    map = L.map("map", { zoomControl: false, worldCopyJump: true }).setView([lat, lng], 4);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: "&copy; OpenStreetMap & CartoDB",
        subdomains: "abcd",
        maxZoom: 7,
    }).addTo(map);

    markerGroup = L.layerGroup().addTo(map);
    addRadarMarker(lat, lng);
    addCoverageCircle(lat, lng, 1000);
    logMessage("🗺️ Map initialized successfully.");
  } catch (err) {
    logMessage(`❌ Error initializing map: ${err}`, "error");
  }
}


function addRadarMarker(lat, lng) {
  const radarIcon = L.divIcon({
    className: "radar-marker",
    html: `<div class='radar-pulse'></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
  radarMarker = L.marker([lat, lng], { icon: radarIcon }).addTo(map);
}

function addCoverageCircle(lat, lng, radiusKm) {
  L.circle([lat, lng], {
    color: "#00ffc3",
    fillColor: "rgba(0,255,195,0.25)",
    fillOpacity: 0.2,
    radius: radiusKm * 1000,
    weight: 1.2,
    dashArray: "4 6",
  }).addTo(map);
}


async function loadSatellites() {
  try {
    const res = await fetch("/api/satellites?radius=90");
    const data = await res.json();
    const info = data.ucs_info || {};

    document.getElementById("ucs-status").textContent =
      `${info.status ?? "Active"} (${info.records ?? 0} registros, ${info.age_days ?? 0} días)`;
    document.getElementById("ucs-date").textContent = info.date ?? "Desconocido";

    markerGroup.clearLayers();
    const list = document.getElementById("sat-list");
    list.innerHTML = "";

    data.satellites.forEach(s => {
      const marker = L.circleMarker([s.lat, s.lng], {
        radius: 5,
        color: "#00b8ff",
        fillColor: "#00eaff",
        fillOpacity: 0.9,
      }).bindPopup(
        `<b>${s.name}</b><br>
         País: ${s.country}<br>
         Propósito: ${s.purpose}<br>
         Usuario: ${s.user}<br>
         Altitud: ${s.alt.toFixed(1)} km`
      );
      markerGroup.addLayer(marker);

      const li = document.createElement("li");
      li.innerHTML = `<span class="sat-name">${s.name}</span>`;
      const details = document.createElement("div");
      details.classList.add("sat-details");
      details.innerHTML = `
        <p><b>País:</b> ${s.country}</p>
        <p><b>Propósito:</b> ${s.purpose}</p>
        <p><b>Usuario:</b> ${s.user}</p>
        <p><b>Altitud:</b> ${s.alt.toFixed(1)} km</p>`;
      li.appendChild(details);
      li.querySelector(".sat-name").addEventListener("click", () => {
        details.classList.toggle("visible");
        map.flyTo([s.lat, s.lng], 5);
        marker.openPopup();
      });
      list.appendChild(li);
    });

    logMessage(`✅ Data synchronized (${data.satellites.length} satellites).`, "success");
  } catch (err) {
    logMessage(`❌ Error loading satellites: ${err}`, "error");
  }
}


document.addEventListener("DOMContentLoaded", async () => {
  await bootSequence();

  
  function updateTime() {
    const now = new Date();
    document.getElementById("datetime").textContent =
      now.toUTCString().replace("GMT", "UTC");
  }
  setInterval(updateTime, 1000);
  updateTime();

  
  const refreshBtn = document.getElementById("refresh-map");
  refreshBtn.addEventListener("click", async () => {
    refreshBtn.disabled = true;
    logMessage("🔁 Manual sync triggered...");
    await loadSatellites();
    refreshBtn.disabled = false;
  });
});
