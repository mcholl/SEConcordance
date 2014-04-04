Approach 2
===
Using /2.2/questions?order=desc&sort=activity&site=christianity&filter=!17Z3JD_ddl4jhdwxHLKp4SiGKUTfKTcoXVmMkSK_z*43F_
I Get:

{
  "items": [
	{
	  "question_id": 16270,
      "title": "Does Catholic doctrine teach that atheists go to heaven, too?",
      "tags": [
        "catholicism"
      ],
      "answers": [
        {
          "is_accepted": false,
          "answer_id": 16273
        },
        {
          "is_accepted": true,
          "answer_id": 16276
        },
        {
          "is_accepted": false,
          "answer_id": 16864
        }
      ],
      "is_answered": true
    },
    {
      "question_id": 26986,
      "title": "Marks of the true church in Protestantism or Catholicism?",
      "is_answered": true,
      "tags": [
        "catholicism",
        "history",
        "protestantism",
        "ecclesiology"
      ],
      "answers": [
        {
          "is_accepted": false,
          "answer_id": 26999
        },
        {
          "is_accepted": false,
          "answer_id": 27058
        }
      ]
    },
    {
      "tags": [
        "communion"
      ],
      "answers": [
        {
          "is_accepted": true,
          "answer_id": 27056
        }
      ],
      "is_answered": true,
      "question_id": 26965,
      "title": "Is the feast of 1 Corinthians 5:8 the same feast as 1 Cor 11?"
    },
    {
      "tags": [
        "bible"
      ],
      "answers": [
        {
          "is_accepted": false,
          "answer_id": 27024
        }
      ],
      "closed_details": {
        "on_hold": true,
        "description": "This question appears to be off-topic. The users who voted to close gave this specific reason:    <ul class=\"close-as-off-topic-status-list\">\r\n        <li>&quot;Questions seeking <b>pastoral advice</b> are off-topic here; your spiritual problems are too important to be left in the hands of random Internet people. See: <a href=\"http://meta.christianity.stackexchange.com/questions/255/pastoral-advice-questions\">Pastoral Advice Questions</a>&quot; &ndash; David Stratton, Caleb</li>\r\n    </ul>",
        "reason": "off-topic"
      },
      "is_answered": false,
      "closed_date": 1396334367,
      "question_id": 27014,
      "closed_reason": "off-topic",
      "title": "Forgiveness in Marriage"
    },
...
etc..


So, I don't really even need to do this call in line with the initial one.
Instead, I look for question changes since the last call, and harvest the data accordingly.

For each question:
	Store the Question ID, Tags, and Status

	Iterate over each of the answers, and update the answers table with the question id here
