# Nomad
Nomad is an easy way for teams to find and secure parking in the busy downtown core. We leverage our relationships with parking operators to simplify the process of all things parking. We'll do the heavy lifting of finding parking, onboarding (and offboarding) your employees, and streamlining payments no matter how big the job. So many parking spots, so little time. Let Nomad's app take the pain out of parking.

https://nomad-parking-app.herokuapp.com/

## Technologies Used
- HTML
- CSS
- Grid styling and components: Semantic UI
- Animation: Vanilla Javascript, jQuery
- Routes and views: Python, Flask
- Server: Heroku
- Schema/databases: Peewee, SQLite, Postgres
- APIs: Stripe and MapBox 

## Inspiration
My inspiration from this project sprung from a book I read once called The Language of Flowers (Vanessa Diffenbaugh). The main character of the book started a florist business called Message, and she used the language of flowers to arrange her bouquets. The idea of using the language of flowers for a floral arrangement business was very intriguing to me and something I wish actually existing. My app, Message, was built as a mockup for how this character might make an online presence for her business.

## Wireframes
![](https://trello-attachments.s3.amazonaws.com/5c9da5af51595772c0571c59/5c9e8df02c4c2d69caf5e99c/d1b1956ed3021d41467358688a57d132/Screen_Shot_2019-04-12_at_4.00.54_AM.png)
Back of napkin wireframes to start

![](https://trello-attachments.s3.amazonaws.com/5c9da5af51595772c0571c59/5c9e8df02c4c2d69caf5e99c/c32271110a904b6e41ebc8702859c348/Screen_Shot_2019-04-12_at_4.01.45_AM.png)
Higher fidelity mockups by Zoe Powell

## Database Structure and ERD

![](https://trello-attachments.s3.amazonaws.com/5c9e5c46d1c46c1b12f5eb85/915x801/ae42d90734adf457083479cbd3a7b22d/Screen_Shot_2019-04-12_at_3.58.59_AM.png)

The database for this project utilizes 5 different interconnected tables, including an external stripe database. Every user that signs up, technically becomes a Customer object in Stripe to allow for future invoices or subscription sign-ups. An admin can sign up a team and point of contact. That client team lead can manage parking for their entire team and retrieve or download invoices with ease. Admins routes and authentication ensures admins control what users can see and do in the app. 

## Challenges and Wins
Some challenges (and wins) with this project were:
- Taking a single form and saving data to multiple locations
- Creating an elegant way to immediately save a Parker id as a variable to then store as foreign key to a Vehicle table without superfluous url params
- Creating a user in stripe first to save a stripe customer id in the User table
- Rendering a dynamic map with parking specifics
- Styling was more of a challenge that I initially scoped

## Code snippets
![](https://trello-attachments.s3.amazonaws.com/5c9da5af51595772c0571c59/5cb0735b28261f0f0e2bd885/2159efbdfb1d656acd304c63009f1568/Screen_Shot_2019-04-12_at_2.38.22_AM.png)

![](https://trello-attachments.s3.amazonaws.com/5c9da5af51595772c0571c59/5cb0735b28261f0f0e2bd885/8def22f81e7ca3550605beb2492f5ee9/Screen_Shot_2019-04-12_at_2.39.31_AM.png)

## Future Developments
This is not a project that ends here. I'm working hard to implement new features throughout the next two weeks to maximize the impact of this MVP. I've conducted user research with my current clients excited to try out the new product. This product exists based on our wish list conversations, and I'm looking forward to the alpha and beta tests with my clients later this month.

