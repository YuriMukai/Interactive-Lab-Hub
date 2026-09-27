# Chatterboxes

**Yuri**

A voice parking assistant: you talk to the car and it parks for you. I designed it and tested it with Wizard of Oz techniques.

---

# Part 1

## A. Text to Speech

**Write your own shell file to use your favorite of these TTS engines to have your Pi greet you by name.**

I used Piper, because it sounded a little more gentlemanly and polite, and it felt like the latest technology. The script is [`speech-scripts/greeting.sh`](speech-scripts/greeting.sh).

**Is the same greeting, in these different voices, the same greeting? Describe one concrete way the voice changed what the utterance seemed to mean or who seemed to be speaking.**

When the voice is different, the same words give a different impression. For example, espeak had no emotion in its voice, and Festival had a low male voice with a rough, mechanical sound, so it felt like the voice of an old machine. Both gave me the impression of an old machine, and that made me imagine a device that detects me coming home with a sensor and says "welcome back" just because a rule tells it to. On the other hand, Piper still sounded like a machine, but it had natural intonation like a car navigation system, so it felt like a modern voice. That made me imagine a personalized home agent that notices I came home and says, "Welcome back, you're late today," as if it understood my feelings and my situation. I think the biggest difference was whether the voice seemed to carry emotion and whether it sounded natural.

---

## B. Speech to Text

**Record a few seconds of your own speech and transcribe it with at least two model sizes. Report the real-time factor for each. At what point does the accuracy improvement stop being worth the delay, for a system that has to answer you?**

I recorded myself for 5 seconds saying "Hello, my name is Yuri. Today is Sunday and the weather is nice." and transcribed it with two models.

| Model | Transcript | Transcription time | RTF |
|---|---|---|---|
| tiny.en | Hello, my name is Yuri, welcome to the next video. | 1.39s | 0.28x |
| base.en | Hello, my name is Yuri, today is Sunday. | 2.33s | 0.47x |

tiny.en was faster, but it replaced the second half with "welcome to the next video," which I never said. base.en was about one second slower, but it heard what I actually said. I think being about one second slower is fine if the result is accurate.

**Write your own script that verbally asks for a numerical input and records the answer the respondent provides.**

My script [`speech-scripts/ask_zip.py`](speech-scripts/ask_zip.py) asks for a zip code, reads back the digits it heard to confirm, and saves the answer. When I said 11101, it sometimes heard 11121. Maybe my pronunciation was part of the problem, but number recognition seemed weak. Speaking one digit at a time with clear breaks made it work more often, but then the pauses sometimes triggered the end-of-turn detection, and the rest was treated as the next sentence.

---

## C. Turn-taking

**Try both extremes, and something in between. Describe what each one feels like to talk to. Note specifically: at 0.2s, what kinds of normal speech get cut off? At 1.5s, what does the delay make the system seem like?**

Results:
- **0.2s:** "I want to order um..." and "Uh, coffee please." were split into two, and my zip code was broken into pieces like "1, 1, 1." and "1, 2, 1." Pauses for thinking ("um") and the breaks between digits were cut off.
- **0.4s:** Sentences were cut in the middle, and meaningless fragments like "head end." appeared.
- **0.7s:** My zip code and my coffee order were captured as one utterance, but when I paused to think, it split into "...but" and "I couldn't."
- **1.5s:** Everything was captured completely and accurately.

Personally, none of them felt very slow with listen.py. Maybe that is because I was not asking a question and expecting an answer. When I tried echo_bot.py, which replies to me, 1.5s felt slower, because I expected a quick reply and had to wait.

---

## D. Storyboard

**Post your storyboard and diagram here.**

**Storyboard:** [View the storyboard](https://drive.google.com/file/d/16jRKrF0B0F8aqmULiY6EmomXOQXDkPt3/view?usp=drive_link)

My device is a voice assistant that parks the car when you ask it to. The storyboard has four panels: arrive and ask → choose a spot → confirm → parked ("Don't forget your bag").

I chose Piper for the voice because it felt like a modern system. Basically, the device always waits about 2 seconds before answering. I used the same wait for yes/no answers and for "stop," because I want to see how the participant reacts. I would also like to separately try a version where the device interrupts the user, and compare the two.

**Please describe and document your process.**

Auto parking systems are not intuitive to operate, so I thought it would be interesting to try controlling one by voice. Also, driving is something that can become very dangerous if one thing goes wrong, so I thought it would be easy to see whether people feel frustrated when they do it by voice.

---

## E. Acting out the dialogue

**Recordings:**
- [Session 1](https://drive.google.com/file/d/1U9dzBW_cCBYgBWoBjwChu8D_Fivl0rSw/view?usp=drive_link)
- [Session 2](https://drive.google.com/file/d/1b3GLwRm8wqWck19GPcDTlxradHoKMByz/view?usp=drive_link)
- [Session 3](https://drive.google.com/file/d/1xYOjqBgOwCRz_Ok4W5SXGv8HpMj7CZmn/view?usp=drive_link)

**Describe if the dialogue seemed different than what you imagined when it was acted out, and how.**

I played the AI agent in front of the participant and watched how they reacted.

- They asked in ways like "Is there anywhere I can park?" and "Could you park?"
- They said "anywhere" for the spot. All I could do was ask whether left or right was better.
- They said "Yes" a lot.
- Unlike my script, they did not hesitate or stumble much, so I never had to interrupt them.
- I made them wait about 2 seconds before answering, but when I asked if the slow replies were frustrating, they said they did not notice at all.
- When I watched the video later, the participant was looking at me a lot, as if checking my reaction. I think they were reading my face to figure out what I was doing: whether I was thinking, listening, or waiting for them to ask for something.

---

# Part 2

## Redesign

- When the driver asks the car to park, the car itself suggests a spot ("This spot is available") and asks for confirmation, because many drivers leave the decision to the car.
- Instead of my face, the participant looks at a screen. I made a UI that shows whether the system is thinking or listening (Listening / Thinking / Checking safety / All clear / Parking / Parked).
- After the safety check, the car asks for a final confirmation: "Should I start parking?"
- The end-of-turn pause is 0.7s, which felt the most natural in Part 1C.
- The top button next to the screen is an emergency stop.

## Prototype: how the system works

**Video (system and controller):** [Watch the video](https://drive.google.com/file/d/1ApytHbG9ts9VF9eS_EbKox-CrWJW_4Bi/view?usp=drive_link)

It is a Wizard of Oz system ([`speech-scripts/parking_wizard.py`](speech-scripts/parking_wizard.py)).

- **Participant (driver):** Sits in front of the Raspberry Pi, looks at its screen, and asks the car to park.
- **Pi (the car):** Listens through the microphone and transcribes speech (listen.py with base.en), and speaks with Piper. The mini screen shows the current state, and it switches to "Thinking" automatically when the driver finishes speaking. The top button stops the car and the bottom button resets.
- **Me (the wizard):** I open the controller in a browser on my PC. While watching what the driver said, I press buttons with scripted lines to make the car speak. For anything not in the script, I type a line in a free text box.
- Every event is logged with a timestamp ([`session_log_person1.jsonl`](session_log_person1.jsonl)).

## Test the system

I could only test with one participant; I was not able to find a second person. So the results below are early observations from a single session.

### What worked well about the system and what didn't?

**What worked:**
- The participant said it was helpful that the screen showed whether the system was thinking or listening.
- They liked the last line, "Don't forget your bag."

**What didn't work:**
- They said they were speaking clearly, but the car did not answer, and it took a long time to reply. The system failed to recognize their voice many times, which frustrated them.
- There was a long gap between when they finished speaking and when the screen switched to "Thinking."
- They were very frustrated that "Listening" never ended. On the other hand, they said a long "Thinking" was still acceptable.
- Being told "Could you say that again?" was frustrating.
- When the car said "Say stop anytime," they thought "stop" was for when the car got too close to something. They did not expect it to mean stopping the whole parking.
- The reaction after saying "stop" was far too slow. They said that in real life, this would be fatal.

**Reflection:**
It was interesting that a long "Listening" was not acceptable, but a long "Thinking" was. Both states were shown on the screen, so I think what matters is not only whether the user can see the situation, but whether they can accept it. When "Listening" does not switch, it looks like the system has not noticed that the conversation ended, so it is not acceptable. When "Thinking" takes a long time, it feels like the AI is thinking in order to give a good answer, so it seems unavoidable.

### What worked well about the controller and what didn't?

**What worked:**
- Because scripted lines were buttons, I could answer quickly without typing. Some buttons also changed the screen automatically, so one press was enough.
- I could see the transcription of what the driver said, so I knew what the system heard (it was often different from what they actually said).

**What didn't work:**
- Because I was right in front of the participant, typing gave away that I was controlling the car.
- I could not see what the Pi screen was showing at that moment, which made things confusing.

### What lessons can you take away from the WoZ interactions for designing a more autonomous version of the system?

- Ending "Listening" a little earlier and switching to "Thinking" would probably reduce frustration. If the user still wants to talk, the system can switch back to "Listening" as soon as they start speaking again.
- When the system cannot understand, it should say "Please say that again" without making the user wait. "Say that again" itself was frustrating, but the most stressful situation seemed to be waiting and then finding out the system had not understood.
- "Don't forget your bag" worked really well. I want to keep in mind how important a small extra phrase like this is.

### How could you use your system to create a dataset of interaction? What other sensing modalities would make sense to capture?

- I could collect logs of what users actually say when they want the car to park. Since each driver utterance is recorded together with the reply I chose as the wizard, the logs could also serve as examples of how an AI should respond.
- Sensors to find open spots to suggest, sensors to check safety, and a sensor that detects the end of speech from mouth movement.