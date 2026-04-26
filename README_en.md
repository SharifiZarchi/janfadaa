# Documentation of the "Janfada" Historical Scandal

The Islamic Republic attempted to demonstrate widespread support by launching the "Janfada" (Soul-Sacrificer) website. Official authorities of the Islamic Republic, including the President, heads of other branches, the IRIB (state media), and government outlets, have repeatedly claimed—citing the website's registration statistics—that over 30 million people have signed up. They used this as "proof" of the public's massive alignment with the Islamic Republic. However, several amateur programming errors on this website led to a major scandal, exposing the actual registration numbers. This repository provides the documents and evidence of this scandal.

---

## 1. Technical Analysis of Identifiers
To display a selection of user messages (hereafter referred to as "comments") on the site, the website uses an Ajax service. Calling this service is easily done by executing the following command in a terminal:

```bash
 curl -s 'https://janfadaa.ir/ajax' --data-raw 'action=getComments' | jq
```

This service constitutes the first mistake made by the website's developers: every record received through this service displays the ID of the records registered on the website. These IDs are ascending integers with a maximum value (at the time of writing) of **3,913,777**. At this very moment, the website claims the number of registrants is over 30 million. Below is a sample response from this service (each response contains 15 comments; 3 are shown here as an example):

```json
{
  "data": {
    "all": [
      {
        "id": 3913777,
        "fullname": "",
        "description": "هرکاری از دستم بر بیاد انجام میدهم برای کشورم",
        "date": "۱۴۰۵/۰۲/۰۵,۱۹:۴۳"
      },
      {
        "id": 3913775,
        "fullname": "",
        "description": "تا پای جان از این انقلاب دفاع خواهم کرد جانم فدای رهبر",
        "date": "۱۴۰۵/۰۲/۰۵,۱۹:۴۳"
      },
      {
        "id": 3913770,
        "fullname": "",
        "description": "من جان \n فدای کشور عزیزم ایران میشوم",
        "date": "۱۴۰۵/۰۲/۰۵,۱۹:۴۳"
      },
      ...
         ],
    "next": 1777138019
  },
  "success": true
}
```

### Translation of the Persian Comments above:
* **ID 3913777:** "I will do whatever I can for my country."
* **ID 3913775:** "I will defend this revolution with my life; my life for the Leader."
* **ID 3913770:** "I sacrifice my life for my beloved country, Iran."

---

## Inaccuracy of State Media Responses

After I exposed this issue in a tweet, state media tried to pretend that the aforementioned ID was a "comment ID" and not a "registrant ID." In doing so, they attempted to claim that while registration records exceeded 30 million, the number of comments was nearly 4 million. However, these media outlets were unaware that the amateur developers left enough evidence in the code to refute this claim.

First, note that there is only one registration form on this website. After entering their full name, mobile number, province, city, date of birth, gender, and education level (most fields being optional), the user can choose to enter a comment. The comment can be empty or contain short text.

It is sufficient to look at the website's source code in the file [`website_snapshot/assets/js/public.js`](website_snapshot/assets/js/public.js?ver=1.5.0). When a registration request is sent, a record is transmitted to the servers as follows:

```javascript
        const data = {
            action: 'verificationSms',
            verificationCode: verificationCode,
            mobile: mobile,
            fullname: fullname,
            state: state,
            city: city,
            birthday: birthday,
            gender: gender,
            education: education,
            description: description,
            formToken: formToken,
        }
```

If we compare the elements in the registration record with the elements in the Ajax output, we see they share common fields including `fullname` and `description`. In reality, when a registration record is sent, the website assigns an `id` and a registration `date` to it in the database. Thus, the `id` is the registration record ID. Since a user can register multiple times, the ID count is higher than the actual number of unique users. But the story doesn't end there.

---

## Analysis of All Retrieved Records

To retrieve all records returned by the Ajax service, you can use the simple script [`crawler.py`](crawler.py), which I wrote with the help of Gemini/Antigravity. If interested, please see the "Technical Details of Record Retrieval" section.

Analysis of these records reveals new facts about this historical scandal:

* The total number of records returned by the website until the preparation of this document is only **1,654 items**, available in the file [`janfadaa_comments_chain.jsonl`](janfadaa_comments_chain.jsonl). The site's secrecy in not displaying the full list of registrants demonstrates the total lack of credibility of its claims.
* The oldest comment with ID `117` was registered on March 28, 2026 (8 Farvardin 1405), and the next comment with ID `1,803,827` was registered on April 8 (19 Farvardin). During this 11-day gap, no other accessible comments exist via the service.
* By observing the irregular intervals of the returned comments (sometimes sequential IDs/times, other times massive jumps even within a 15-message block), it becomes clear that only a very small number of comments were **hand-picked** by the website administrators for display. Why does this matter? The answer is in the next section.

---

## Identical Long Messages

Within these 1,654 accessible comments, there are messages repeated twice or more. While generic messages like "My life for Iran" are expected from different users, it gets interesting when long, unconventional texts are found:

> **Persian:** جانم فدای رهبرم سید مجتبی خامنه ای\nلبنان نباید تنها بماند\nایران بامعرفت همانطور که لبنان در کنارش ایستاد باید در کنارش بماند
>
> **English:** My life for my leader Seyyed Mojtaba Khamenei. Lebanon must not remain alone. Noble Iran must stand by Lebanon just as Lebanon stood by it.

This specific comment was registered on two different days:
* 2026/04/10, 20:25, `id=2277832`
* 2026/04/11, 14:08, `id=2494010`

Given the long and unusual nature of this text, it was certainly submitted by the same source. This might not seem strange—perhaps one user copied and pasted it twice. However, the key point is this: considering the tiny percentage of comments exposed by the site (only 1,654) and the massive gap between the two IDs (over 200,000 units), the fact that two identical long comments were "hand-picked" by the admins leaves only one possibility: **The volume of duplicate registrations was massive and likely automated.** Even while hand-picking a tiny number of comments, the administrators could not prevent the exposure of this systematic fraud.

Other examples of identical, long, and unusual comments in this small set include:

> **Persian:** میان دشمن و وطن ننگ بر آنکه شک کند \nننگ بر آنکه خواسته شمر به ما کمک کند\nجانم فدای ایران🇮🇷♥️
>
> **English:** Shame on whoever wavers between the enemy and the motherland. Shame on whoever wants "Shimr" (the villain) to help us. My life for Iran 🇮🇷♥️

> **Persian:** من به عنوان یک شهروند ایرانی حاضرم جانم را فدای وطنم کنم.
>
> **English:** As an Iranian citizen, I am ready to sacrifice my life for my country.

---

## They Don't Understand Numbers

The evidence of this massive historical scandal is not limited to these cases. The greatest evidence is the website's lack of transparency. If these statistics were true, the administrators would have published anonymized records (removing names and phone numbers) from the start.

In my opinion, this scandal stems from several factors. For instance, Islamic Republic officials assume the public has low intelligence, believing that by repeating false claims daily and creating an information vacuum through internet shutdowns, they can convince people they have 30 million supporters. Yet, Iranians learn the truth very quickly via social media. 

Furthermore, the website claims to only register individuals over 12 years old. The population over 12 in Iran is estimated at 70–73 million, millions of whom are abroad and generally cannot register. A claim of 30 million registrants implies that **one out of every two Iranians over the age of 12** living in the country has signed up. The designers of this move didn't even imagine that anyone could realize the absurdity of this claim through a simple poll of their own neighbors.

One only needs to look at the near-linear growth of the announced stats (up to 26 million, after which they slowed the growth pattern slightly). Had no one stopped them, they would have soon claimed 100 million registrations. All this scandal stems from one bitter truth: **The officials of the Islamic Republic do not understand numbers.**

---

## Reproduction
To reproduce these results, simply run [`crawler.py`](crawler.py). Please review the following technical details:

* **Security:** If you wish to ensure your IP is not logged by this regime-owned website, it is highly recommended to use a proxy or VPN (e.g., Tor). Change the `USE_PROXY` variable to `True` at the beginning of `crawler.py` and specify your proxy port.

---

## Technical Details of Record Retrieval

One can use the Ajax service and change the `pointer` value to save all records returned by the service. This is done by taking the `next` value from a returned record and using it as the pointer for the next request. For example:

```bash
curl -s 'https://janfadaa.ir/ajax' --data-raw 'action=getComments&pointer=1777138019' | jq
```

Here, `1777138019` is the `next` value from the previous response. There is a small technical glitch: the amateur programmers wrote the service such that it returns no response for certain valid `pointer` values. This challenge can be solved with a bit of logic.

The key observation is that `pointer` values are always descending, though they don't follow an obvious pattern at first glance. To solve the "dead-end" issue, whenever a `pointer` returns nothing, we can subtract a fixed amount (e.g., 100 units) and try again. In this case, even if the pointer isn't exact, the service maps it to the nearest valid value and returns the output.

Running this program reveals that 14 `pointer` values (specified in [`broken_pointers.txt`](broken_pointers.txt)) hit a dead end, equivalent to 14 blocks or 210 user comments. Retrying a thousand times via [`broken_pointers_retry.py`](broken_pointers_retry.py) yielded no results. Regardless, missing these 210 extra comments does not change the overall findings.