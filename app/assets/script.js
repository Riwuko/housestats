var delayInMilliseconds = 10000; 

setTimeout(function() {
        const element = document.querySelector('.offer-hyperlink');

        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === "attributes") {
                    element.innerHTML =`Offer url: ${element.href}`;

                }
            });
        });

        observer.observe(element, {
        attributes: true //configure it to listen to attribute changes
        });
        
}, delayInMilliseconds);


