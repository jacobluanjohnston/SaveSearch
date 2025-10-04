# SlugSaver

* Hi, we're SlugSaver. We want to make grocery shopping smarter for UCSC students and Santa Cruz residents.

### PROBLEM:
* Right now, finding the best deals means either driving to multiple stores or manually flipping through flyers, seeing tons of irrelevant sales.

### SOLUTION:
* An AI-powered parser that automatically extracts every deal from local grocery store flyers that they send and upload weekly. We made it searchable in one place.

### DEMO:
* `python3 -m http.server 8000`
* Visit http://localhost:8000/
* Use the search function, view sales, type of sales, and the grocery store location. Compare across grocery stores in one place!

### TECH:
* At first, we tried conventional scraping. But it got way too complicated. These flyers, especially Safeway's, were built with confusing layouts, almost as if they want to resist scrapers. So then we switched to using Claude AI API to scrape the weekly sales and put them into .csv and .json formats. The Safeway was ~80% accurate and New Leaf was 100% accurate.

### IMPACT:
* Save time, save money, don't waste time being tempted by food sales that you don't want, and reduce food waste by knowing exactly what's on sale before you shop. Perfect for anyone on a budget. 

That's SlugSaver! Grocery deals, simplified.

### PROBLEMS:
* This was the core functionality and it took very long optimizing for accuracy. It took up a majority of the time. The Safeway weekly sales are not accurate yet.

### WHAT'S NEXT:
Improvement:
* Get Safeway's weekly ads to >99.5% accuracy
* Continue testing upcoming weekly ads from New Leaf and Safeway grocery stores.
* Incorporate CostCo, Whole Foods, and others.
Core functionality we wished we got to:
* Create alerts and subscriptions for sales for your favorite items or necessities.
* Ability to scan and upload reciepts to track your purchases over time automatically to see where you save or wasted money.
Additional features:
* Track sale trends over time and predict trends.
* Incorporate regular (non-sale) items for a fully-fledged database. Find ways to scrape this while honoring robots.txt.
* Incorporate other items other than grocerys and edibles.
