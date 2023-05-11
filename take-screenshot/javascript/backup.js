var takeScreenshot = {
	tabId: null,
	screenshotCanvas: null,
	screenshotContext: null,
	scrollBy: 0,
	size: { width: 0, height: 0 },
	originalParams: { overflow: "", scrollTop: 0 },
  
	initialize: function() {
	  this.screenshotCanvas = document.createElement("canvas");
	  this.screenshotContext = this.screenshotCanvas.getContext("2d");
	  this.bindEvents();
	},
  
	bindEvents: function() {
	  chrome.browserAction.onClicked.addListener(function(tab) {
		this.tabId = tab.id;
		chrome.tabs.sendMessage(tab.id, { msg: "getPageDetails" });
	  }.bind(this));
  
	  chrome.runtime.onMessage.addListener(function(request, sender, callback) {
		if (request.msg === "setPageDetails") {
		  this.size = request.size;
		  this.scrollBy = request.scrollBy;
		  this.originalParams = request.originalParams;
		  this.screenshotCanvas.width = this.size.width;
		  this.screenshotCanvas.height = this.size.height;
		  this.capturePage(request.position);
		}
	  }.bind(this));
	},

	capturePage: function(position) {
	  	var self = this;
	  	setTimeout(function() {
			chrome.tabs.captureVisibleTab(null, { format: "png" }, function(dataURI) {
		  		if (typeof dataURI !== "undefined") {
					var image = new Image();
					image.onload = function() {
						self.screenshotContext.drawImage(image, 0, position);
						var croppedCanvas = document.createElement("canvas");
						var length = self.screenshotCanvas.height;
						croppedCanvas.width = length - 200;
						croppedCanvas.height = length - 200;
						var croppedContext = croppedCanvas.getContext("2d");
						croppedContext.drawImage(
							image = self.screenshotCanvas, 
							sx = (self.screenshotCanvas.width - length) / 2 + 100, 
							sy = (self.screenshotCanvas.height - length) / 2 + 100, 
							sWidth = length - 200, 
							sHeight = length - 200, 
							x = 0, 
							y = 0,
							width = length - 200, 
							height = length - 200
							);
						var a = document.createElement("a");
						a.download = "cropped-screenshot.png";
						a.href = croppedCanvas.toDataURL("image/png");
						a.click();				
					};
					image.src = dataURI;
				}
			});
		}, 300);
	}
};

takeScreenshot.initialize();
