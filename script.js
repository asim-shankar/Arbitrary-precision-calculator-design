let display = document.getElementById("expression");

function appendChar(char) {
  display.value += char;
}

function clearDisplay() {
  display.value = "";
}

async function calculate() {
  try {
    let res = await fetch("http://127.0.0.1:5000/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expression: display.value })
    });

    let data = await res.json();
    if (data.result) {
      display.value = data.result;
    } else {
      display.value = "Error";
    }
  } catch (e) {
    display.value = "Error";
  }
}
