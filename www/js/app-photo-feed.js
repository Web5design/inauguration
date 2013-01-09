$(document).ready(function() {
    var POLLING_INTERVAL = 120000;
    var PHOTO_CATEGORIES = ['latest', 'npr-picks', 'i-voted-for-you', 'i-didnt-vote-for-you', 'id-rather-not-say-how-i-voted', 'i-didnt-vote']


    function ISODateString(d) {
        function pad(n) {
            return n < 10 ? '0' + n : n
        }

        return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate()) + 'T' + pad(d.getUTCHours()) + ':' + pad(d.getUTCMinutes()) + ':' + pad(d.getUTCSeconds()) + 'Z'
    }

    function update_backchannel(first_run) {
        /*
         * Update the backchannel from our tumblr feed.
         */
        $.getJSON('live-data/misterpresident.json?t=' + (new Date()).getTime(), {}, function(data) {
            for (var i = 0; i < PHOTO_CATEGORIES.length; i++) {
                var category = PHOTO_CATEGORIES[i];

                var posts = data[category];
                var posts_length = posts.length;
    
                var $photos = $("#photos-" + category);

                for (var j = 0; j < posts_length; j++) {
                    var post = posts[j];

                    // Old
                    // if (post.id in posts_html) {
                    //     // Changed
                    //     if (html != posts_html[post.id]) {
                    //         el.show();
                    //         $posts.find("#post-" + post.id).replaceWith(el);

                    //         if (post.type === "regular") {
                    //            has_tweets = true;
                    //         }
                    //     }
                    // // New
                    // } else {
                    //     $posts.prepend(el);

                    //     el = null;
                    //     el = $posts.find("#post-" + post.id)

                    //     if (first_run) {
                    //         el.show();
                    //     } else {
                    //         el.slideDown(1000);
                    //     }

                    //     el.find(".tstamp").timeago();
                    //     el = null;

                    //     if (post.type === "regular") {
                    //         has_tweets = true;
                    //     }
                    // }

                    // posts_html[post.id] = html;
                    $photos.append('<img src="' + post.photo_url + '"/>');
                }

                // $posts.find(".post:nth-child(5)").nextAll().remove();
            }
        });
    }

    update_backchannel(true);
    setInterval(update_backchannel, POLLING_INTERVAL);
});