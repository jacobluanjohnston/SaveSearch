# SlugSaver
<img width="839" height="634" alt="Screenshot 2025-10-04 at 4 12 57 PM" src="https://github.com/user-attachments/assets/2192f190-8834-4432-9efc-7b670bd59cc3" />



* Hi, we're SlugSaver. We want to make grocery shopping smarter for UCSC students and Santa Cruz residents.

### PROBLEM:
* Right now, finding the best deals means either driving to multiple stores or manually flipping through flyers, seeing tons of irrelevant sales.

### SOLUTION:
* An AI-powered parser that automatically extracts every deal from local grocery store flyers that they send and upload weekly. We made it searchable in one place.

### DEMO:
* `python3 -m http.server 8000`
* Visit http://localhost:8000/
* Use the search function, view sales, type of sales, and the grocery store location. Compare across grocery stores in one place!

### PROBLEMS/TECH:
* At first, we tried conventional scraping. But it got way too long and complicated and started eating into a lot of time. These flyers, especially Safeway's, were built with confusing layouts, almost as if they want to resist scrapers. 
* So then we switched to using Claude AI API to scrape the weekly sales and put them into .csv and .json formats. The Safeway was ~80% accurate and New Leaf was 100% accurate, but that took a lot of time editing the prompt and checking outputs to optimize to that level.

### IMPACT:
* Save time, save money, don't waste time being tempted by food sales that you don't want, and reduce food waste by knowing exactly what's on sale before you shop. Perfect for anyone on a budget. 

That's SlugSaver! Grocery deals, simplified.

### WHAT'S NEXT:
Improvement:
* Get Safeway's weekly ads to >99.5% accuracy
* Continue testing upcoming weekly ads from New Leaf and Safeway grocery stores.
* Incorporate CostCo, Whole Foods, and others.
Core functionality we wished we got to:
* Create alerts and subscriptions for sales for your favorite items or necessities.
* Ability to scan and upload receipts to track your purchases over time automatically to see where you save or wasted money.
* Automatic scheduled jobs to download weekly ads and scrape when they come out rather than manually downloading ads and scraping locally with commands.
* UI and front end design
Additional features:
* Track sale trends over time and predict trends.
* Incorporate regular (non-sale) items for a fully-fledged database. Find ways to scrape this while honoring robots.txt.
* Incorporate other items other than grocerys and edibles.
