/**
 * Send the "takeScreenshot" message when the button on popup.html is pressed.
 */
document.getElementById("takeScreenshot").addEventListener("click", function () {
    chrome.runtime.sendMessage({ msg: "takeScreenshot" });
});
