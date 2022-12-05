(function( global, factory ) {

    if ( typeof module === "object" && typeof module.exports === "object" ) {
            // For CommonJS and CommonJS-like environments where a proper window is present,
            // execute the factory and get jQuery
            // For environments that do not inherently posses a window with a document
            // (such as Node.js), expose a jQuery-making factory as module.exports
            // This accentuates the need for the creation of a real window
            // e.g. var jQuery = require("jquery")(window);
            // See ticket #14549 for more info
            module.exports = global.document ?
                    factory( global, true ) :
                    function( w ) {
                            if ( !w.document ) {
                                    throw new Error( "jQuery requires a window with a document" );
                            }
                            return factory( w );
                    };
    } else {
            factory( global );
    }

// Pass this if window is not defined yet
}(typeof window !== "undefined" ? window : this, function( window, noGlobal ) {

    jQuery.event.handlers = function( event, handlers ) {
        var sel, handleObj, matches, i,
                handlerQueue = [],
                delegateCount = handlers.delegateCount,
                cur = event.target;

        // Find delegate handlers
        // Black-hole SVG <use> instance trees (#13180)
        // Avoid non-left-click bubbling in Firefox (#3861)
        if ( delegateCount && cur.nodeType &&
                ( event.type !== "click" || isNaN( event.button ) || event.button < 1 ) ) {

                /* jshint eqeqeq: false */
                for ( ; cur != this; cur = cur.parentNode || this ) {
                        /* jshint eqeqeq: true */

                        // Don't check non-elements (#13208)
                        // Don't process clicks on disabled elements (#6911, #8165, #11382, #11764)
                        if ( cur.nodeType === 1 && (cur.disabled !== true || event.type !== "click") ) {
                                matches = [];
                                for ( i = 0; i < delegateCount; i++ ) {
                                        handleObj = handlers[ i ];

                                        // Don't conflict with Object.prototype properties (#13203)
                                        sel = handleObj.selector + " ";

                                        if ( matches[ sel ] === undefined ) {
                                                matches[ sel ] = handleObj.needsContext ?
                                                        jQuery( sel, this ).index( cur ) >= 0 :
                                                        jQuery.find( sel, this, null, [ cur ] ).length;
                                        }
                                        if ( matches[ sel ] ) {
                                                matches.push( handleObj );
                                        }
                                }
                                if ( matches.length ) {
                                        handlerQueue.push({ elem: cur, handlers: matches });
                                }
                        }
                }
        }

        // Add the remaining (directly-bound) handlers
        if ( delegateCount < handlers.length ) {
                handlerQueue.push({ elem: this, handlers: handlers.slice( delegateCount ) });
        }

        return handlerQueue;
}


}));
