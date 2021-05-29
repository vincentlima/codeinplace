# codeinplace
my final project for Code in Place, a wonderful class I took
Here’s a fun fact I realized while coding. Do you know how many unique sets of 75 items you can pull out of 100? While my program was busy crashing my computer, I calculated the answer: about 243 sextillion sets. That’s 2 times 10 with 23 zeroes.
So I gave up on my original bright idea of iterating through every combination.
Here’s what my code is for: In my work, which is to make exams fair, I sometimes have to cut questions out of an exam.
If we’re developing a 50-question exam, we might beta-test it with 60 or 70 questions.
This program recommends a list of questions to remove from the exam to achieve the target length while it maximizes one parameter, known as alpha.
It follows content constraints, so that there aren’t too many or too few questions in any content domain.
After I restarted my computer, I came up with a more practical way to solve my problem. Instead of trying every unique set of, say, 75 questions, I have the program find the best set of 99 out of 100. Then the best 98 out of 99. And so on, until the problem is solved. So very much faster!
