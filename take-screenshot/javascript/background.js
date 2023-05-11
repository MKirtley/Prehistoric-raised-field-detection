/**
 * This class takes a screenshot of a portion of the current browser window and saves it as a PNG image.
 */
class TakeScreenshot {
  constructor() {
    this.tabId = null; // The ID of the currently active tab.
    this.screenshotCanvas = document.createElement("canvas"); // A canvas element used to store the captured image.
    this.screenshotContext = this.screenshotCanvas.getContext("2d"); // The 2D context of the screenshotCanvas canvas.
    this.size = { width: 0, height: 0 }; // An object that contains the width and height of the captured image.
    this.bindEvents(); // Bind event listeners to Chrome APIs.
  }

  /**
   * Binds event listeners to Chrome APIs.
   */
  bindEvents() {
    chrome.runtime.onMessage.addListener((request, sender, callback) => {
      if (request.msg === "takeScreenshot") {

        // When the "takeScreenshot" message is received, query the active tab in the current window.
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {

          // Set the tabId to the ID of the active tab.
          this.tabId = tabs[0].id; 

          // Send a message to the content script requesting the page details.
          chrome.tabs.sendMessage(this.tabId, { msg: "getPageDetails" });
        });
      } else if (request.msg === "setPageDetails") {

        // When the "setPageDetails" message is received, store the page size and update the canvas size.
        this.size = request.size;
        this.screenshotCanvas.width = this.size.width;
        this.screenshotCanvas.height = this.size.height;

        // Call the capturePage function to take the screenshot.
        this.capturePage();
      }
    });
  }

  /**
   * Captures the visible tab, crops the resulting image, and saves it as a PNG file.
   */
  capturePage() {
      chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataURI) => {
        
        // Check if the dataURI is defined.
        if (typeof dataURI !== "undefined") {

          // Create a new Image object.
          const image = new Image();
          image.onload = () => {
            
            // Draw the captured image onto the screenshotContext.
            this.screenshotContext.drawImage(image, 0, 0);

            // Create a new canvas element to store the cropped image.
            const croppedCanvas = document.createElement("canvas");
            const length = this.screenshotCanvas.height;
            croppedCanvas.width = 512;
            croppedCanvas.height = 512;
            const croppedContext = croppedCanvas.getContext("2d");

            // Draw the cropped image onto the croppedContext.
            croppedContext.drawImage(
              this.screenshotCanvas,
              (this.screenshotCanvas.width - length) / 2 + 200,
              (this.screenshotCanvas.height - length) / 2 + 200,
              length - 200,
              length - 200,
              0,
              0,
              length - 200,
              length - 200
            );

            // Create an anchor element, set the download attribute and href, then simulate a click to download the image.
            const a = document.createElement("a");
            a.download = "cropped-screenshot.png";
            a.href = croppedCanvas.toDataURL("image/png");
            a.click();
          };

          // Set the source of the image to the dataURI received from the captureVisibleTab callback.
          image.src = dataURI;
        }
      });
  }
}

// Instantiate the TakeScreenshot class.
const takeScreenshot = new TakeScreenshot();
