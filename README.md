# RSSanitize

RSSanitize proxies an RSS feed while performing on the fly sanitization of the text in the feed.

## Motivation

The W&W Rave Culture Radio podcast includes HTML entities which violate the XML specification.  This causes my podcast player (Pocket Casts) from parsing the feed and downloading new episodes.

## Inspiration

[RSS-lambda](https://rss-lambda.xyz/)

[xkcdmobile](https://www.miserez.org/ws/xkcdmobile/)

## Usage

Running the application will automatically create an rss.xml web endpoint which returns the sanitized podcast feed.

## Development

Open in VSCode, then run `flask run --reload`

The webapp will be available at [localhost:5000](http://localhost:5000)