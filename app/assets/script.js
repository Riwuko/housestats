var delayInMilliseconds = 1000; //1 second

setTimeout(function() {
        const element = document.querySelector('#on-click-graph-data');

        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === "attributes") {
                    // window.open(element.href)
                    element.innerHTML =`Offer url: ${element.href}`;

                }
            });
        });

        observer.observe(element, {
        attributes: true //configure it to listen to attribute changes
        });
        
}, delayInMilliseconds);


