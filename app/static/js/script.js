const paths = document.querySelectorAll(".json");
paths.forEach((i) => {
  let show = false;
  i.addEventListener("dblclick", () => {
    if (show) {
      i.classList.remove("show");
    } else {
      i.classList.add("show");
    }
    show = !show;
  });
});
