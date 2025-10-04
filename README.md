SlugSaver

Hi, we're SlugSaver. We want to make grocery shopping smarter for UCSC students and Santa Cruz residents.

PROBLEM:
Right now, finding the best deals means either driving to multiple stores or manually flipping through flyers, seeing tons of irrelevant sales.

SOLUTION:
I built an AI-powered parser that automatically extracts every deal from local grocery store flyers that they send and upload weekly. We made it searchable in one place.

DEMO:
`python3 -m http.server 8000`
Visit http://localhost:8000/
Use the search function, view sales, type of sales, and the grocery store location. Compare across grocery stores in one place!

TECH:
At first, we tried conventional scraping. But it got way too complicated. These flyers, especially Safeway's, were built with confusing layouts, almost as if they want to resist scrapers. So then we switched to using Claude AI API to scrape the weekly sales and put them into .csv and .json formats. The Safeway was ~80% accurate and New Leaf was 100% accurate.

IMPACT:
Save time, save money, don't waste time being tempted by food sales that you don't want, and reduce food waste by knowing exactly what's on sale before you shop. Perfect for anyone on a budget. 

That's SlugSaver! Grocery deals, simplified.

WHAT'S NEXT:
This was the core functionality that took very long. But what's next is alerts, subscriptions, and the ability to upload receiepts to track your purchases over time to see where you save the most.
