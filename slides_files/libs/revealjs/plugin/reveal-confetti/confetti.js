var script = document.createElement("script");
script.setAttribute("type", "text/javascript");
script.setAttribute(
  "src",
  "https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"
);
document.getElementsByTagName("head")[0].appendChild(script);

function getPosition(event) {
  posX = event.pageX;
  posY = event.pageY;
}

document.addEventListener("mousemove", getPosition, false);

window.RevealConfetti = function () {
  return {
    id: "RevealConfetti",
    init: function (deck) {
      deck.addKeyBinding({ keyCode: 65, key: "A" }, () => {
        const config = deck.getConfig();
        const options = config.confetti || {};

        confetti({
          particleCount: options.particleCount,
          angle: options.angle,
          spread: options.spread,
          startVelocity: options.startVelocity,
          decay: options.decay,
          gravity: options.gravity,
          drift: options.drift,
          ticks: options.ticks,
          colors: options.colors,
          shapes: options.shapes,
          scalar: options.scalar,
          zIndex: options.zIndex,
          disableForReducedMotion: options.disableForReducedMotion,
          origin: {
            x: posX / window.innerWidth,
            y: posY / window.innerHeight,
          },
        });

        console.log(`posX: ${posX} | posy: ${posY}`);
        console.log(options);
        console.log("🎊🎉");
      });
    },
  };
};
