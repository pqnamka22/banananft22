const tg = window.Telegram.WebApp;
tg.expand();

function pay() {
  const amount = document.getElementById("amount").value;
  tg.sendData(`pay:${amount}`);
}
