/**
 * Listen for messages from the background script.
 */
chrome.runtime.onMessage.addListener((request, sender, callback) => {
  if (request.msg === "getPageDetails") {
    // Calculate the width and height of the page.
    const size = {
      width: Math.max(
        document.documentElement.clientWidth,
        document.body.scrollWidth,
        document.documentElement.scrollWidth,
        document.body.offsetWidth,
        document.documentElement.offsetWidth
      ),
      height: Math.max(
        document.documentElement.clientHeight,
        document.body.scrollHeight,
        document.documentElement.scrollHeight,
        document.body.offsetHeight,
        document.documentElement.offsetHeight
      ),
    };

    // Send a message to the background script with the size and originalParams.
    chrome.runtime.sendMessage({
      msg: "setPageDetails",
      size: size
    });
  }
});
