const addGoBackButton = function() {
    const back = document.createElement("a");
    back.href = "./";
    back.textContent = "< Go-back";
    back.style.position = "fixed";
    back.style.bottom = "10px";
    back.style.left = "10px";
    back.style.zIndex = 9999;
    back.style.color = "black";
    back.style.backgroundColor = "white";
    back.title = "Go back to the index page ...";
    document.body.appendChild(back);
};

const allowInputCodeCollapse = function() {
    const codeCells = document.querySelectorAll(".jp-CodeCell .jp-Cell-inputArea");
    for (let codeCell of codeCells) {
        let collapser = codeCell.previousElementSibling;
        collapser.textContent = "-";
        collapser.style.cursor = "pointer";
        collapser.style.fontWeight = "bold";
        collapser.style.display = "block";
        collapser.style.lineHeight = "2em";
        collapser.onclick = () => {
            if (collapser.textContent === "-") {
                collapser.textContent = "+";
                codeCell.style.display = "none";
            } else {
                collapser.textContent = "-";
                codeCell.style.display = "block";
            }
        }
        collapser.click();
    }
};

window.onload = function() {
    addGoBackButton();
    if (is_jupyter) {
        allowInputCodeCollapse();
    }
};
