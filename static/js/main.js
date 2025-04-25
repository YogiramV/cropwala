async function getCoimbatoreWeather() {
  const city = 'Coimbatore';
  const apiKey = '0d8ab73f63907b8635c71366446aaf0b';
  const weatherURL = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`;

  try {
    const weatherResponse = await fetch(weatherURL);
    const data = await weatherResponse.json();

    if (String(data.cod) === "200") {
      const weatherHTML = `
        <div class="weather-info">
          <div class="temp-main">
            <div class="title">
              <h3>${Math.round(data.main.temp)}°C</h3>
              <p>Feels like: ${Math.round(data.main.feels_like)}°C</p>
            </div>
            <img src="https://openweathermap.org/img/wn/${data.weather[0].icon}@2x.png" alt="Weather Icon" />
          </div>
        </div>
      `;

      document.getElementById('weatherResult').innerHTML = weatherHTML;

    } else {
      document.getElementById('weatherResult').innerHTML = `<p style="margin-top: 30px">❌ Unable to load weather for Coimbatore</p>`;
    }

  } catch (error) {
    document.getElementById('weatherResult').innerHTML = `<p>⚠️ Error fetching data for Coimbatore.</p>`;
    console.error('Fetch error:', error);
  }
}

// Call this on page load
window.onload = getCoimbatoreWeather;
