var select = document.getElementById("id_tipo");
var options = document.getElementById("options-group");

function change_value(value) {
  if (value === "B") {
    options.setAttribute("hidden", "");
  } else if (value === "O") {
    options.removeAttribute("hidden");
  }
}

change_value(select.value);

select.addEventListener("change", (e) => {
  change_value(e.target.value);
});

