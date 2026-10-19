# ACP × Model Risk × Governance-by-Design — Alignment Session (Transcript)

> **Component**: `governance-intake` · **Type**: Artifact (meeting transcript)
> **Status**: Verbatim record — 12 August 2026, 05:02pm, 53m 06s

*In plain terms: this is the raw record of the meeting. Decisions and actions are extracted in [2026-08-12-decisions-and-actions.md](2026-08-12-decisions-and-actions.md); the sequenced plan is in [2026-08-12-governance-alignment-roadmap.md](2026-08-12-governance-alignment-roadmap.md).*

Auto-transcribed by Microsoft Teams. Lightly cleaned for sentence breaks only — wording is unchanged. Transcription artefacts remain (e.g. “OFSVI”/“officer” = OSFI, “ICP”/“ECP” = ACP, “laying views”/“length views” = Langfuse, “Catherine” = Kathryn, “nurture” = in Archer).

## Attendees

| Person | Role in this conversation |
|---|---|
| Seth Chalmers | ACP Product — chaired the session |
| Kathryn C Vandenberg | Governance-by-Design lead |
| Duncan Wyllie | Governance-by-Design — assessment module, intake |
| Ryan Bolick | CMRM / Model Risk — obligations, metric selection guide |
| Colin Bell | Engineering leadership |
| Mark Jarvis | Technology risk / MBCT |
| Kalyan Adhikari | Evidence storage, tooling standardisation |
| Robert Chin | Asked where the data is managed |
| Anirban Ukil | Deployment / orchestration |
| Adam Love | Attendee |
| Niall Kirk | Attendee |

## Topic index

| Time | Topic |
|---|---|
| 0:05 | Opening — why the internal MVP paused and Luminate became the go-forward codebase |
| 2:52 | Deployment and orchestration |
| 5:02 | How building on the Consortium changes things — engine upstream, Sun Life content as configuration |
| 7:33 | Reusable risk-classification module — who owns the content, who owns the API |
| 10:57 | Policy-as-YAML — and the rename to “obligations” |
| 14:54 | ACP as the canonical record; Archer is a downstream sync, not a dependency |
| 16:14 | Validation requirements — turning obligations into gates |
| 18:28 | Human-first, then codify |
| 21:21 | What information at what stage of maturity |
| 23:15 | Where does the data live? APM records and Archer |
| 25:54 | Evaluations and evidence |
| 27:36 | Are we duplicating artifacts? |
| 30:43 | Archer’s model-validation section as the final store |
| 32:33 | Could a synthetic Archer unblock us? |
| 35:05 | Colin’s three layers of evaluation and observability |
| 38:50 | Different audiences — use cases vs agents vs the product itself |
| 40:36 | What drives Governance-by-Design requirements |
| 41:45 | Reporting split — OSFI E-23 from ACP, technology risk from GbD |
| 42:26 | Composable agents — assessing at application and agent level |
| 43:28 | Overlapping tooling and evidence-producer adapters |
| 49:00 | Standardise or stay open — a baseline suite, not a mandate |
| 50:08 | Metric library and judge calibration |
| 51:55 | Wrap-up and follow-ups |

---

## Transcript

### Opening — why the internal MVP paused and Luminate became the go-forward codebase

**Seth Chalmers** · 0:05

There we go. All right. Thanks everyone for joining. So wanted to get the gang back together on all of these items that we had kind of going on in the internal build for the ACP. We had some work going on with governance by design and Ryan. on like a new intake form. We had some talks about risk classification modules, evaluation frameworks, basically mobilizing on Ryan's guide that he has for metrics and how to select them and integrating those with the ACP. We had a lot of screens and UI development that were done in our internal build, and basically all of that has paused at this point. For anyone who's not aware, we've moved over to the consortium build like we were just talking about. We've got that deployed. in dev. We've got the engineering team mobilized in the consortium, getting an idea of how we make these changes in the Luminate code base, which is going to be the go forward code base. I am working on right now the first kind of spec that we want, an implementation that we want to move over, which is in relation to all of these items. So it's what we're dubbing the governance mode. This is how we do the OFSVI and NIST reporting, integrate with the evaluation framework, the governance intake form, all of the approvals and stuff we're talking about with the MVP, how we move that over to the Luminate code base. And so that's why I wanted to get thismeeting together and identify who's owning these kind of artifacts that can kind of drive code that's implemented in the ACP and essentially where those things live, how we deliver on them programmatically. There's a lot of. documents and confluence pages and SharePoints and things like that that should probably move to get repos and actual applications that we can deliver on on the ACP. So that's kind of the purpose of this document. So I've kind of gone throughall of the items that we want to align on. It's a lot of items. So, and this is all just draft based on what we're working on in the MVP. So as I'm going through this, please interject, ask any questions, things like that. This is howI'm kind of proposing we can do this. It doesn't mean it's set in stone or how it needs to be done. So pause there. Yep, go for it.

### Deployment and orchestration

**Anirban Ukil** · 2:52

So the first is, yeah, Seth, one question, like, as I see the platform, the first question comes, like, do you have any visual on the deployment strategy? Like, if we are using EKS or OpenShift, where the runtime is getting deployed, where, like, do you have any visual on? how this is getting deployed, like we see it working, but what is the like mechanism that it's being deployed to?

**Seth Chalmers** · 3:21

Yep, so we have like full CICD pipelines, helm charts, et cetera. I think Colin and like Greggo are working on all the approvals of how that looks like. But we're deploying it across a bunch of different environments that, like Colin mentioned, need to be approved. So right now it's just in dev. We have test, stage, prod.

**Anirban Ukil** · 3:29

Okay.

**Colin Bell** · 3:31

Yeah.

**Seth Chalmers** · 3:39

stood up. So we're looking to promote that across the environments once everything's in place.

**Colin Bell** · 3:45

Yeah, and I think, Anirban, we've got some items to kind of map out that by...A commitment that by the 21st, we'll have kind of ACP on a page draft one out. Yeah, so we have to run with that one to kind of explain because there's in a slide that we took to DBTS ET today, we have a number of the kind of decisions that need to be made documented. So I'll bounce that slide deck to you.

**Anirban Ukil** · 4:01

Exactly, yeah. So the. Okay, okay. OK, perfect, because the reason being, if we zoom in, yeah, yeah, if we zoom in, the discussion that we had, if we put this one zoomed end layer, that this is how ACP looks like, and I think that would give the picture a solid boost.

**Colin Bell** · 4:17

But that was kind of scrambled together end of last week. Yeah, yeah. Yeah, we have to bring all the work you've been doing on the various orchestration approaches and then layer them on top of this so that we have, these are the different ways you can build agents. This is how the agents talk to the things through the ACP, and this is the handful of questions we have about how we're going to deploy them in.

**Anirban Ukil** · 4:40

Exactly. Yeah.

**Colin Bell** · 4:52

In production, so...

**Anirban Ukil** · 4:54

Yeah, okay. Thank you, because I'm working on that, so I thought if we can march into that and it, okay, that's the plan. Perfect.

**Colin Bell** · 5:00

Yeah, yeah, yeah.

### How building on the Consortium changes things — engine upstream, Sun Life content as configuration

**Seth Chalmers** · 5:02

Yeah, and I'll link all of our specs and stuff under Ben after this on the deployment and things like that as well for your reference. And so just one thing I wanted to call out, what's different than the MVP build? Obviously with an internal build, we could quickly make changes. It was kind of exactly adapted to what our requirements were, what we were feeding it. like from Ryan, all of your documentation and things like that, how this kind of changes in the consortium build is that we're kind of building towards like very generalizable, configurable modules to be implemented in Luminate, and then abstract all of Sun Life specific concepts. into configuration that is driving the ACP content screens in Luminate. So we now have to kind of build more generically. We need to determine what are those specific sunlight artifacts, how are they driven into this process and configurable. deliver within the Luminate code base that functionality, and then on the Sun Life side and the product team side, go and test it with our Sun Life specific configuration. So that's kind of the semantics we'll get into as we divide things between like what is, where do things live in the consortium,Where do things live on model risk, governance by design, or the product team as well? And so, as I mentioned before, what we want to move towards is all of these artifacts that are driving this to versioned configuration in Git repositories and applications that we can iterate on. And so just first out of the gate, the reusable risk classification module. So we've got a lot of great questionnaires, content coming out of model risk, kind of a scoring matrix. What we want to seeis this risk classification module being an ACP kind of programmatic implementation and have these questionnaire contents configuration driven by model risk. I'm not sure if this is also in governance by designs roadmap as well. Yep, Kathryn.

### Reusable risk-classification module — who owns the content, who owns the API

**Kathryn C Vandenberg** · 7:33

Yeah, I think you're probably anticipating my questions. I agree model risk is really key here, but there are other risk domains involved. And we had looked at an agent risk classification that included those perspectives as well. I think, Ryan, your team is taking a look at where that landed. right now for for your for your perspective and to map it back to some of the thinking that your team had done as well. Is that right?

**Ryan Bolick** · 8:02

Yeah, so Mohamed sent over the proposal and we're looking at that now, and it basically encompasses like most of the model risk questions and adds in a few few other dimensions, and we're kind of looking at that, make sure it aligns with what we'd expect, and we'll have some feedback for you soon.

**Kathryn C Vandenberg** · 8:19

Okay, yeah, that's great. So I think then, Seth, the call out here is that while the model risk and architecture perspectives are key, that there are some other considerations when thinking about risk tiering outside of the model risk and architecture spaces that we're trying to incorporate into sort of an overall risk scoring mechanism that is under review right now.

**Seth Chalmers** · 8:42

Makes sense. And so on the governance by design side, are you looking to maintain kind of like an API for this risk classification module or that's something that we should be doing on the ACP product team? How do you see that happening?

**Kathryn C Vandenberg** · 8:59

I think that's more Duncan's area than mine. I don't know about what is the right way to manage that. Duncan, I think you've got some initial thinking on that.

**Duncan Wyllie** · 9:09

Yeah, we've got an assessment module, which would include, I guess, kind of consolidated questions, which can then be used to create templates. And then the risk scoring engine can be applied to that as well. And then, yeah, we could expose that. By our API, if you want, so for I guess kind of the risk domain, oh sorry, the model risk, they would those questions can get added to that repository and then an API to to extract them and. But maybe we could take that offline and see how that could operate. But we've got more questions in addition to model risk that we want to capture in a standard way. So.

**Seth Chalmers** · 9:53

Okay, so you know me, Duncan, I want to get rolling on this right away. So are we thinking maybe this is a, well, we can take this away, but the actual programmatic exposing this as an API, maybe this is something that this is kind of fundamental to the. the ACPs kind of operation within the registries and all that, but I don't want the content being driven by the ACP. Like obviously you guys are coming up with things, Model Risk is coming up with things. Is this something the ACP product team can maintain that API interface, but all of the configuration, the...markdown files, whatever everyone is collaborating on to produce, those are config that is fed into this application.

**Duncan Wyllie** · 10:45

Yeah, I think we, yeah, probably take this away because I wanted to speak to you about this anyway. So yeah, I think we can kind of have a sidebar conversation and figure out the best way. So.

### Policy-as-YAML — and the rename to “obligations”

**Seth Chalmers** · 10:57

Yeah, that sounds great. So I'll move on from that one. So next one, Ryan again has come up with a lot of policy as YAML configuration. So essentially like what does a Gen. AI use case, what does it need to satisfy before it can be? released. There's lots of work on already, obviously having it as YAML files. These can drive policies and what we'd like to sort of integrate into the ACP in terms of what governance status is a particular agent or model at, and what environments should it be able to be deployed to. So this is another example kind of following along the same format where we don't want to be determining what these policies are necessarily, but just the general framework of how these policies map to different gates that allow agents or models to be deployed. to different environments. Yep.

**Kathryn C Vandenberg** · 12:10

Yeah, just I think a similar comment here. There are requirements for AI use cases that come from other risk domains as well as model risk. We are currently building an intake that will manage sort of the risk tiering and routing on an automatedbasis that I think could feed into this. Ryan, what are your thoughts?

**Ryan Bolick** · 12:32

Yeah, I think a similar approach could be taken for other risk areas. So like we could even like piggyback off of the kind of the conventions here. I've labeled kind of the different, or I want to rename that instead of calling it policies, probably call it obligations just to not confuse it with our act.

**Kathryn C Vandenberg** · 12:36

Yeah. Yeah, I was gonna, I was gonna ask about that, but yeah, okay.

**Ryan Bolick** · 12:51

But you could have, like, in theory, you could have, you know, like a privacy set of obligations that kind of gets put into this kind of policy as code implementation. You could have all the different domains kind of define their own specific requirements, right? And then it could follow a similar type of approach, right?

**Kathryn C Vandenberg** · 13:09

So I think the I think my call out here, Ryan, is that we've already consult like collected and consolidated requirements from a workflow standpoint across all of the various teams. I think there's probably more work to do. Obviously, there's more complexity that's introduced from a for agents than there is for AI use cases. But I do think that we need to stay consistent across governance by design requirements and ACP requirements and make sure that we're carrying converse like the right information across both of them so that we're talking together effectively. In my view, given that where we've embeddedmodel risk in the governance by design workflows, my desire would be to embed your requirements in a consistent way and governance by design and have those two systems talk to one another and ensure that those integrations into Archer and what gets documented is consistent across the two systems. I think we're going to need to have a conversation about whatthat full Archer integration and an oversight from a model risk standpoint looks like, but I think this is probably a bit of a triangle.

**Ryan Bolick** · 14:25

Yeah, that makes sense. I think that with all the, you know, there has to be alignment between all three areas properly for sure. Yeah.

**Kathryn C Vandenberg** · 14:29

Yeah. Yeah, and I'm making an assumption that we should probably validate that a lot of your requirements can be met through a governance by design front door, and then through follow through with build and registration through the AC, and you know, monitoring, et cetera, through the ACP.

**Ryan Bolick** · 14:50

Yeah, that makes sense.

**Kathryn C Vandenberg** · 14:50

We'll see. We'll have to validate, but those are the assumptions that I'm making right now.

### ACP as the canonical record; Archer is a downstream sync, not a dependency

**Seth Chalmers** · 14:54

Yeah, and then like from an ACP perspective, we need to be the canonical record for everything that's produced, like decisions that are made for agents, models, where they're deployed to, traces gathered, evidence produced, etc. And we had those conversations on that bi-directional sync. between Archer and the ACP. I don't think it makes sense to make, just based on the timelines and everything for Archer, getting access to their APIs as an example, to pin ourselves on the Archer integration. So ultimately things need to be happening in the ACP. we can gather and produce an evidence report from the ECP, but definitely once those integrations are in place, sync back to Archer eventually. Yeah.

**Kathryn C Vandenberg** · 15:46

And agreed. And I think it's worth noting too, Seth, just for awareness that one of our objectives in governance by design is to be able to provide to our oversight bodies a full governance lineage. So including inclusive of the entire solution. So as we, you know, gain more maturity, Iwant to make sure that we're keeping that in mind so that we can build that end-to-end visible lineage that can be shared through automated reporting. And I think a lot of that data is going to be in the ACP and we should talk about how that information is generated for oversight.

### Validation requirements — turning obligations into gates

**Seth Chalmers** · 16:14

Right. Absolutely, yep. So summary, what I'm getting from this, have governance by design kind of drive, get the model risk requirements, make sure this policy registry is populated. This is probably another instance where the ACP can maintain an API or module. that pulls all this information together to be utilized within the ACP screens and registries and things like that. So we'll have some further conversations on what all these sources look like, how we integrate with them, and then what that integration in the ACP screens and any governance by design lineage as well. Looks like. Great. Um...And so...This is kind of related already. I think we talked about some of this. But...Yeah, I think this is overlap. Let's move on. And so then we get to things like validation requirements. So what do all these policies mean into a check that has to pass before anything proceeds? And so I was wondering what...this kind of looks like, and Ryan, you've mapped out what this looks like, and if we can have low risk models, like what are those gates and what are those bands? And ultimately, this also needs to be kind of a module that is produced and has all these gates for. when we need evidence, when we need human in the loop approvals, like what does that kind of look like today?

### Human-first, then codify

**Ryan Bolick** · 18:28

Yeah, I'm actually working on like, so we had these high level kind of policies I sent you along, but I'm actually working on a lot more granular sort of like assessments for each of those that we could, you know, have actionable kind of success criteria for and things like that. And the idea is that like I was sharing screen give a flavor of it. But the idea is that at first, like the whole process will be, will go through like humans, right? So like, it'll be like a human, human first driven process and then give it an example, right? So like the output quality evaluation, there's like a set of like 15 questions I'd want them to answer and then provide evidence for. And then basically there would be like a then a human review aspect of it here, where they're going and confirming it's true. But then like we'd have each of these policies, there would be kind of a series of criteria, right, that they would need to go through. And then we can. have a bit of a more defined rubric around kind of like if these criteria are met, right? So.

**Seth Chalmers** · 19:33

So kind of like, let's start with more of a human intervention process and build towards what exactly those validation policies look like.

**Ryan Bolick** · 19:43

Right, well, this is like, so basically I'm building out kind of like the process to follow, and I think this will get translated into what we get an agent could eventually kind of ingest at that level, but I'm just kind of building out kind of like what needs to be followed, you know, at a very granular level so that like a...you know, a validator who's not familiar with the process could reasonably follow the instructions and go through the process. So I'm thinking that'll be translatable to like what an agent would expect, that level of information. So, yeah.

**Seth Chalmers** · 20:17

And then just to connect the dots, so would this look like a UI screen like we had in the MVP with that full like intake questionnaire according to what you've got here? Or what does that look like from a evaluator perspective and where should that live?

**Ryan Bolick** · 20:34

So the way, so basically there's like an upfront documentation ingestion step, right? So like you would go through making sure that all of these components are fulfilled, right? So you've got like a change log, basically assumptions and methodology documentation. So that would be the first step is kind of just making sure all the information is needed for the system. and then we'd have kind of like, you can have deterministic checks kind of do this even, but you probably won't like an agent to assess the quality just to make sure it's not just like kind of garbage information. But then you would have kind of these later assessments, which then take those, that documentation as prerequisites. And then that's where kind of the moreI think granular guidance is needed too, so yeah.

### What information at what stage of maturity

**Kathryn C Vandenberg** · 21:21

I think there's an interesting opportunity here, which is aligned with some of the other work that we were doing, Ryan, around, which I think you were there for, which was what information do we need at what stage of maturity, right? So like, what do we need for intake? What do we need an initial approval and evaluations? What do we need? in the interim and it looks like some of the stuff that you've got here are kind of mid-level too. Like what are you, what's your access control documentation, like that type of thing. I think there's some. There's an interesting opportunity here because I suspect that other governance domains will be very interested in that information as well. So would love to partner with you on, you know, your vision for that information capture and flow and what your reviewers need, because I think this also dovetails into some of our end-to-end.

**Ryan Bolick** · 22:01

Yeah.

**Kathryn C Vandenberg** · 22:14

our end-to-end strategy and the work that Duncan is executing against right now with more of a focus on architecture. And then like how could we package up the information that we're collecting generically more meaningfully for model risk? So I think there's that's an interesting topic. And then how doesall of that information feed into the ACP from a governance approval standpoint so that the builder knows that they've got license to build the agent and what's been approved. And then once the agent is built, then like how does ACP send out the information on testing that you're asking for? So I think we're, you know, this is sort of back to the beginning, which is like, what is that end-to-end workflow? What is the, you know, where do approvals need to occur? When does build happen? And then how do we validate testing and where does the information go afterwards to report on that kind of end-to-end lineage? I think there's some, you know, Seth, I think this is super timely. Thank you for booking the meeting.

**Duncan Wyllie** · 23:12

Yeah.

### Where does the data live? APM records and Archer

**Robert Chin** · 23:15

I guess we're still working on where all this data is going to be managed. All those sections. Is that still in progress?

**Kathryn C Vandenberg** · 23:21

Yeah, thanks Rob. That's also a question I have too.

**Robert Chin** · 23:23

Like it's not in Archer, right? Or like all the sections that we've talked about here. Yeah. So we're looking for a new home for this.

**Kathryn C Vandenberg** · 23:27

Or just just model registry, right? So, yeah.

**Ryan Bolick** · 23:31

The old. I mean, the ultimately the validation like evidence would get stored in Archer, but and kind of the registration information for the use cases and the risk and the model risk risk classification. So, those three items I think are the main thing that would go in Archer. One thing that also we've been looking at is trying to...

**Robert Chin** · 23:45

Mhm.

**Ryan Bolick** · 23:53

tie kind of technology dependencies more elegantly to Archer, I guess. And one of the things we're thinking about was trying to maybe tie it like APM records to use cases in Archer. And that way it would just be, it would allow us to kind of filter by kind of the underlying platforms that are being used for the use cases more easily and. rather than trying to recreate some kind of like concept of a platform level record nurture, which I think would be a bit redundant. So that's something that we're thinking about too.

**Duncan Wyllie** · 24:26

And that's something where as part of our intake of being able to capture kind of like references to APM is something that we're also looking at as well. So if we're feeding into your use cases, hopefully you should have some of that information that you could inherit and then pass on to Archer.

**Seth Chalmers** · 24:27

Yeah.

**Duncan Wyllie** · 24:45

Sam.

**Ryan Bolick** · 24:46

That'd be great, yep.

**Seth Chalmers** · 24:48

Yeah, and then for the actual, like all of those items that you're showing there, Ryan, and when I was glancing through them, like I think we can work towards kind of like this view where we have a policy registry. So turning all of those requirements into YAML files, whatever it is, layered on with some. code as well to determine these gates, like when are things blocked, when is it satisfied, etc. When do we need human in the loop approval, have it fully codified as policy, and then ultimately produce these validation reports that Catherine is mentioning, like when is everything supplied, when is it not, what do you need to do to get to production, that sort of thing.

**Ryan Bolick** · 25:31

Yeah, that sounds that sounds great. I think that makes a lot of sense. Essentially, you would have like just certain gates that require like certain prerequisite documentation to be there and then it kind of move forward in the process from there, right?

**Seth Chalmers** · 25:32

Sorry. Exactly, yeah, according to the risk classification and everything. Maybe if it's very low risk, we don't need to do most of the steps, that sort of thing.

**Ryan Bolick** · 25:52

Yeah.

### Evaluations and evidence

**Seth Chalmers** · 25:54

Awesome. All right, that brings us to evaluations and evidence. So I think this is one of the main consortium contributions. We also want to work towards this evaluation framework that we were kind of enabling on the registries and the ACP. So this is according to a risk band, what evaluations need to be done. Ryan, again, you've done a lot of great work on what this looks like. Helper utilities for metric selection and all that. I think all that we want to continue building intoscreens, as well as the product team on the ACP is coming out with a kind of agent harness for how you configure your agents to work with the ACP. So once we get these evaluations, which we can kind of take your recommendations and turn that intocode so you can basically take these evaluations and according to what has been identified as risk for your particular agent, this is how you, what metrics you should start selecting. This is how you can start enabling them in whatever platform you want to do that in, open layer, laying views, anything else, bedrock evaluations, anything that's coming out. So I think we'll just eventually just keep working towards this. And then those evidence packages also need to be producible by the ACP. So the, yeah, Kalyan.

### Are we duplicating artifacts?

**Kalyan Adhikari** · 27:36

I was just thinking that these platforms like...bedrock evaluation are open layer, they will produce the artifacts after evaluating the use case. Now, how do we tie those? To a use case or a risk, the requirement that you know led to those artifact creation and the schedule in which the artifacts will be created, and where are we? Are we saying even land use? Are we saying that we will? you know, will show through ACP as a consolidated view of those artifacts or are we porting it, you know, those artifacts and you know, letting users download those artifacts. The point I'm trying to make Seth, are we duplicating the same artifacts in ACP or not? So that's what my question is.

**Seth Chalmers** · 28:41

Yep, it's a great question. So bear with me. This is a bit involved in how this comes together. But the gist of it is that it needs to be driven through the ACP's registries. We had the concept of an Archer control domain in the MVP that we worked with Ryan on. This is how we map.

**Kalyan Adhikari** · 28:46

Yeah.

**Seth Chalmers** · 29:03

a bunch of agents or a bunch of models back to that Archer AI use case. And so when we have agents registered, models registered, we have risk bands calculated, we can determine what evaluations need to be placed. Those are also artifacts in the registry themselves. So

**Kalyan Adhikari** · 29:24

Okay.

**Seth Chalmers** · 29:24

what evaluations are required, what's the cadence, et cetera. And then once all of that's in place, it's driven by the ACP's registry, we have knowledge of what Archer AI use cases it pertains to, what agents are allowed to call other agents, what are all the evaluations that need to be run and at what cadence. And then once all of that's in place, then we had our concept of the evaluation API that allows all of these overlapping and conflicting tools like OpenLayer, LangFuse, Bedrock evaluations, et cetera, to just become. evidence producers that are normalized within the ACP. And so ultimately, the evidence needs to be stored in the ACP and the registries there. So that when we're in the ACP UI, we want to generate an officer report, we can pull up all of the evidence. So exactly what that looks like, like it probably doesn't make sense, obviously, to be duplicating data everywhere. There can be data in workload accounts that is staying in workload accounts, but ultimately it needs to come back to the ACP.

**Kalyan Adhikari** · 30:40

Okay.

### Archer’s model-validation section as the final store

**Robert Chin** · 30:43

Does this fit in with your validation section in Archer, Ryan? Because you have a validation section where you go through the model validation, right? Like results. Is that what goes in there? Actually, I've never done one.

**Ryan Bolick** · 30:56

Sorry, what was the first part that you said?

**Robert Chin** · 30:57

Oh, you know, you know what the, in actually there's that section model validation. The people.

**Ryan Bolick** · 31:01

Yeah, that's where all the reports are stored and attached to, yeah.

**Robert Chin** · 31:04

Yeah. Do you use that as your reporting to regulators?

**Ryan Bolick** · 31:10

Yeah, that's our like kind of just system record that we would store all of our validation evidence in, yeah.

**Robert Chin** · 31:16

So we would need to push our stuff into there, or would you get stuff from ACP? Or are we gonna have one?

**Ryan Bolick** · 31:22

It'll need to live in Archer as the final spot. Yeah, so I think ICP would be the mechanism to collect all that evidence and then package it up and then store it in Archer.

**Robert Chin** · 31:26

Okay. Drop it in there, OK.

**Seth Chalmers** · 31:34

Yeah, so back to the one of the earlier points, like integrating with our at this point is very difficult, like getting access to do this sync, but ultimately I think going forward, like ACP needs to obviously have all this evidence that we can produce a report. But then, yeah, we were working towards a Archer adapter, essentially, that can take things in the ACP's registry and sync them back to Archer or vice versa. So if like an AI use case is produced in Archer, we can decompose that into a set of agent registries and. model registry entries as well. So all that was in the plans, but we need to work through that API integration. But just one thing, like it kind of needs going forward has to be done in the ACP so that ultimately we don't have any dependencies on producing that final report.

### Could a synthetic Archer unblock us?

**Ryan Bolick** · 32:33

Is there, Seth, if we, if like, given kind of the challenges in getting the archer access, I think that we'd like, is there like a synthetic archer we could like use it to like mock it up or something like something like that in the meantime? Or like, what's the approach there to essentially? You know, not make Archer be the the blocker, I guess.

**Seth Chalmers** · 32:57

Yeah, so it's just leaning into the ACP's registries. So ultimately we have all of the information that is being synced back to Archer. So that's already in the ACP's architecture and implementation. So we'll store the evidence at the linkages to that, the Archer control domains eventually. will also be in the registry as well as a metadata item. And then we can use the utility to sync back to Archer once all that implementation's in place. So ACP is the canonical record. Everything's produced there. We don't have any dependency on Archer, but once we can get that API integration going. we sync back to Archer and have that bi-directional sync as well if we want to allow people to go through the current process, get things in Archer, decompose an AI use case into a set of agents and models that are then registered in the ACP.

**Kathryn C Vandenberg** · 33:54

I have a question, Ryan, around...The enterprise system of record in terms of runtime facts that a governance report needs in terms of like evaluations, approvals, decisions, governance and audit trail, are you doing ongoing monitoring in Archer today? And is the expectation that you will...that Archer will accommodate those needs. And the follow on question to that is, can we provide that within the construct of what we're planning in governance by design, because we will be collecting all of that data anyway. Sonot something to, I mean, you can answer now if you want to, but you don't have to. But I think it's something that we can explore given what we're intending governance by design to be. and and work with you around how we capture the data, because they, the other, you know, as Seth is talking, we do need to consume the ACP data as well. Colin.

### Colin’s three layers of evaluation and observability

**Colin Bell** · 35:05

So I'm just, and maybe we just need to nail some language. There's three parts, I think, of scanning and evaluation observability that are captured here, right? There's the, there's at registration.

**Kathryn C Vandenberg** · 35:18

Mhm.

**Colin Bell** · 35:24

where we need to assess the risk, figure out what kind of evaluation is needed, perform that kind of onboarding evaluation. Then based on the risk, current kind of evaluations that are scheduled and then the ongoing operations of the system, right? So I think

**Kathryn C Vandenberg** · 35:43

Yes.

**Colin Bell** · 35:44

As I understand it, like...We need to have good records available to, like, if shows up for at, like, at onboarding and at the scheduled intervals running, but then for any particular inference that happens,if we have a client or someone show up and say, why did I get denied or whatever, and I think we're seeing more and more of these come out into the market today, that's where we need to be able to pull that specific execution and get kind of the observability end to end or the context graph end to end of that. that particular use, right? Is that, are we all on the same page, that there's kind of those 3 layers of evaluation we need to be able to support?

**Kathryn C Vandenberg** · 36:33

Yeah, yeah, absolutely. Yeah, I'm not challenging that at all. What I am saying is that the strategy and vision of Governance by Design was intended to capture data and make it available across the entire life cycle. So we are at intake and onboarding today, and that is where we're starting.

**Seth Chalmers** · 36:34

Yep.

**Colin Bell** · 36:35

Okay.

**Kathryn C Vandenberg** · 36:54

But the idea was that while the right systems are being built, you know, architecture is, you know, reimagining ASD. There's the ongoing ACP registration monitoring, ongoing testing. The idea was that all of that data would be. aggregated and reported. through governance by design across the lifecycle. Now, that's not going to happen today, but I think it's important to talk about kind of who does what and what does that path forward look like.

**Colin Bell** · 37:30

Yeah, you'd be able to.

**Kathryn C Vandenberg** · 37:30

Because I don't, yeah, sorry, go ahead.

**Colin Bell** · 37:32

You'd be able to find that an agent was onboarded or, you know, on model use was approved. You'd be able to find all the records that go along with that approval. You'd be able to see the evaluation, the official kind of at launch and ongoing evaluation evidence that's been

**Kathryn C Vandenberg** · 37:35

Mhm.

**Colin Bell** · 37:52

kind of pushed into Archer and then if there's a particular use or a particular kind of execution of that, then it would be digging into the actual application itself and pulling from like operational observe like observability records. Okay, so that then you'd be.

**Kathryn C Vandenberg** · 38:05

That's right. That, yeah, that's correct now.

**Colin Bell** · 38:11

you want to have the aggregation at those top two, but not into the gory details. That's where, okay.

**Kathryn C Vandenberg** · 38:16

Exactly. Yes. Yes. Thank you for for articulating that, Colin. I appreciate it.

**Colin Bell** · 38:21

No, no, that's okay. I just wanted to make sure it was clear there.

**Kathryn C Vandenberg** · 38:25

Yeah, yeah, no, I'm...

**Colin Bell** · 38:25

Uh, so Mark, your your hands up.

**Seth Chalmers** · 38:26

Sam.

**Mark Jarvis** · 38:28

Yeah, no, I think I'm going to take it down. I think you may have articulated it well for Catherine, but I got confused, so we'll take it offline so I don't derail it. I don't derail this.

**Colin Bell** · 38:36

Yeah, yeah, yeah. Sounds good.

**Seth Chalmers** · 38:39

No, so I'll keep it. I'll keep it going. I'll keep it going.

**Robert Chin** · 38:39

Yeah, I think there's definitely different audiences. Yeah, and we don't want to overload and over pollute your needs, Ryan and Archer.

**Kathryn C Vandenberg** · 38:46

Yeah, sorry, I'll try and be quiet now. I'm just, yeah.

**Seth Chalmers** · 38:50

No, I.

### Different audiences — use cases vs agents vs the product itself

**Mark Jarvis** · 38:50

Yeah, I know. I think my quick two cents was I want to also make sure, like, from our view, there's like there's use cases and there's agents, and then there's the actual product itself, and making sure that, like, I don't not everybody needs all of them type of thing, so I, and I think it's just trying to sort that out.

**Seth Chalmers** · 39:10

So I think this is probably one of our major disconnects though. So I'm also, I agree with all those layers, but also confused about where it should live. Because ACP is collecting basically all of this information across all of the layers at this point. We're going to have registration of agents.

**Kathryn C Vandenberg** · 39:10

Yes, agreed.

**Seth Chalmers** · 39:31

models, MCP tools. We're going to be running all of the traffic through a gateway. So we're collecting all of the observability, the traces, why agents are making certain decisions. And then we're also must kind of gather all of the evidence. So we'll have SDKs for how that evidence is produced and normalized within the ACP. So then I guess the question is like, what is happening in governance by design and where does that report automatic end up being generated and who consumes it?

**Kathryn C Vandenberg** · 40:09

Mhm.

**Seth Chalmers** · 40:24

Okay. Okay, that clears up. Yep.

### What drives Governance-by-Design requirements

**Robert Chin** · 40:36

by design going to be driven by an architecture or an IT directive, Catherine? The requirements like Mark Ryan, I know you're driven by the regulators, right? Like, got to keep us out of jail, you're driven by those things.

**Kathryn C Vandenberg** · 40:43

Mhm. Yeah, we follow the Sun Life policies. There's 6 policies and I can't remember them off the top of my head, but the MBCT policy is one of them. So technology risk policy. Sorry, go ahead, Mark.

**Mark Jarvis** · 40:55

Yes, it's. Yeah, I was going to say, it's primarily, I would say it's primarily driven by technology, right? And I think those technologies touch some other risks. So MBCT is an easy one. Privacy, I mean, that's compliance is another one. But then, you know, certainly all the other technical risks that are there. I think what

**Kathryn C Vandenberg** · 41:10

Yeah.

**Robert Chin** · 41:11

Okay.

**Mark Jarvis** · 41:19

Yeah, we want to be careful because there's like 30 other risks that aren't handled by this and it and it's just, it's only, it gets technology embedded.

**Kathryn C Vandenberg** · 41:23

Yeah.

**Robert Chin** · 41:31

Because yeah, folks are trying to figure out what should they prioritize and as they start moving forward with their agent stuff, which directives they should prioritize first in terms of meeting as the onboard ACP. So that's kind of why I was trying to figure that out.

**Kathryn C Vandenberg** · 41:31

Yes.

### Reporting split — OSFI E-23 from ACP, technology risk from GbD

**Seth Chalmers** · 41:45

And so if I can play that back, it would still be useful to produce some type of OSFI NIST report for a particular agent or model, but it's also useful for governance by design to consume that information to produce an overall report for an application or use case or something like that.

**Kathryn C Vandenberg** · 42:05

Correct, yeah.

**Duncan Wyllie** · 42:05

Yeah, we would be a consumer of your data products, essentially.

**Seth Chalmers** · 42:06

Okay.

**Kathryn C Vandenberg** · 42:09

Yes. Yeah. And so, yeah, from my perspective, I think probably E23 reporting is, you know, taken care of by ACP at a high level, whereas some of the other OSFI reporting, when they're looking at technology risk, might be better reported out of governance by design.

**Seth Chalmers** · 42:09

That makes sense. Okay.

### Composable agents — assessing at application and agent level

**Colin Bell** · 42:26

And I think I think if we have that kind of cardinality, all the relationships, it means that when we when and if we get to the point where we have composable sub agents that are approved to take on certain tasks and applications stitch together multiple agents to solve.

**Seth Chalmers** · 42:27

Makes sense. Yeah.

**Colin Bell** · 42:49

A problem, then we'll be able to evaluate at the we'll be able to assemble at the application level and at the individual agent level, which means we can kind of separate the assessment and make sure that we can see how things are performing at both levels.

**Kathryn C Vandenberg** · 43:05

Okay.

**Seth Chalmers** · 43:06

Right.

**Colin Bell** · 43:06

That makes sense. That's like, that's down the, that's a long way in the future, I think. I don't think we're getting to composable agents for a bit.

**Seth Chalmers** · 43:08

Yeah.

**Kathryn C Vandenberg** · 43:12

Yeah, I and the only reason I'm pushing so hard on it now is like I just don't want us to go too far down down a road that we'll have to correct later.

**Colin Bell** · 43:21

Yeah.

**Kathryn C Vandenberg** · 43:22

Or at least if we do, we've decided to do it.

### Overlapping tooling and evidence-producer adapters

**Seth Chalmers** · 43:28

Makes sense. Yeah, thank you. That definitely cleared everything up for me on that. So I think we touched on the overlapping tooling. Kalyan, does this kind of make sense for how we integrate all the evidence producers and move towards that model?

**Kalyan Adhikari** · 43:45

Yeah, yeah, yeah, we. We got our answers. We'll just work on the efficient way of storage of those artifacts. That is an offline discussion we can do. Great.

**Seth Chalmers** · 43:59

Awesome, yeah. Yep, so that'll be in the ACP. Yeah, let's work on exactly what that looks like. Um...And so I guess the only other thing to mention there, so right now this evaluations API kind of exists. It's developed. This is something we'd look to integrate into the consortium. What this looks like in sort of like a product team versus consortium engineering team. sort of breakdown is we'll obviously look to move this functionality over there. If it's all generic, which this kind of evidence producer framework is, but the product team can kind of continue to maintain the harness which allows. different teams to utilize whatever evidence producer they desire to produce that evidence and ultimately have it end up in the ACP by routing everything through a gateway or utilizing the APIs. Um...And then this. Yeah, so that was basically, go ahead.

**Kalyan Adhikari** · 45:17

Said, do we just a comment on that? evidence provider adapters that ACP has to build like. At some point, we have to decide whether or not there are few standard evidence providing tools, right? Otherwise, if there is any number of evidence provider tool picked by...throughout the enterprise and that will be also an operational nightmare, right, to maintain those adapters and the quality or the type of evidence that is being produced. So like we have to standardize. What evidence providers are we using? Just like OpenLayer is a tool. Are we saying OpenLayer and LangFuse will cover that evaluation? Or do we, you know, make room for other tools just for evaluation? Right, so enterprise-wide wise, how are we looking at the evaluation and how is it being produced in different business group? Or is there a strategy so that the harnesses that we have to build is not infinite kind of?

**Seth Chalmers** · 46:46

Yeah, so I see your hand. The advantage of this type of framework is that we can kind of allow anyone to use whatever tool they desire, as long as they're consuming the evaluation APIs to get that information into. the ACP. So this is like purposefully implemented so that we don't have to care. I can see a lot of tool sprawl. There's a lot of open source frameworks that Ryan's explored, you've explored. Every platform is coming out with their own evaluation frameworks. We've got open layer.

**Kalyan Adhikari** · 47:09

In. You. Yeah.

**Seth Chalmers** · 47:27

We've got Langfuse, which is internally managed by the ACP. It's utilized for a bunch of other functionality, but also used for evidence producing. So it's kind of a messy landscape. And what this kind of architecture allows us to do is kind of not care what tools people use.

**Kalyan Adhikari** · 47:37

Yeah.

**Seth Chalmers** · 47:48

And it is most of these frameworks kind of follow the same sort of format. So with OpenLayer, it's a pretty simple like webhook integration to start ingesting all of the evaluations and things like that. And so what we had in the internal build is kind of taking Ryan's guidance. And then you could assign different ones and kind of export your evaluations and it would just give you the configuration that you could copy and paste into your harness or your tool of choice to run that evaluation. So I think we can kind of handle that, but I definitely see where you're coming from. Like it doesn't make sense for Sun Life to maintain.

**Kalyan Adhikari** · 48:19

Yeah.

**Seth Chalmers** · 48:32

all of these tools, I don't think.

**Kalyan Adhikari** · 48:34

Yeah, because we are coming full circle. If we are saying we need these kind of evidences and that is being driven by governance and compliance requirements, then the standardization of tool also is a question in front of us, right? Colin. You may have something to say on that. Are we standardizing the evaluation process or keeping it open for? Yeah.

### Standardise or stay open — a baseline suite, not a mandate

**Colin Bell** · 49:00

So, I think that that's probably more Mark and Ryan. I don't think we're in a position to standardize everywhere, although I think we want to offer a standard suite of tools, but we don't want to force a standard because, like, if we start getting into multimodal...

**Kalyan Adhikari** · 49:13

Yeah.

**Colin Bell** · 49:20

type stuff where there's different types of models being composed with like inference. I don't want to be like, oh, you can't evaluate from there and so you can't do that. Like there, I think the onus, if I understand correctly, Mark, within the policy is like the model owner is ultimately responsible. So if they determine that they need to do something else to manage the risk. I don't, I don't want us to be responsible to. to change everything, but I want to make a baseline evaluation system that captures 80% of the workloads easily usable so that people don't need to think about it and people don't go looking for their own approach to do it.

**Kalyan Adhikari** · 50:05

Kill them.

**Mark Jarvis** · 50:05

You said you summed it up very well, Colin.

### Metric library and judge calibration

**Ryan Bolick** · 50:08

Yeah, and that's kind of the framework that we've put together is it really just gives people a starting point around kind of some best practices to follow around like selecting the metrics that are applicable to their use cases. So one thing I'm curious about, Seth, is do we have any mechanisms in place around likelike a metric library to show for basically, because like we need to make sure that like these metrics are calibrated with appropriately. And so if people are kind of using kind of uncalibrated element as a judge, I think we'd want to be able to identify that and just making sure that they're following, they're actually testing their judges, that sort of thing, right?

**Seth Chalmers** · 50:48

Yeah, so yeah, I took your guidance, turned it into a UI page, all of the helpful information that you passed along to configure each of these metrics. They can be directly imported and laying views, which is what I was testing with the internal build. So I'd look to do the exact same thing and illuminate and essentially port.

**Ryan Bolick** · 50:49

The.

**Seth Chalmers** · 51:08

all of this over. I think this is a really useful mechanism what you've done here. Basically have this metric library that people can evaluate and then once we get to this full like automated risk classification module policy as code, we can say like we need to assign these evaluations for these agents within the registry, have all of it running. It can be done in open layer or in our centrally managed length views in the ACP. So definitely want to continue with this model and move everything over to Luminate.

**Ryan Bolick** · 51:44

Yeah, sounds good.

### Wrap-up and follow-ups

**Seth Chalmers** · 51:55

Cool. We speed ran through all of the items. It's amazing. So the only other things we wanted to go over are kind of the ownership, the follow-up items. I think we've got another bunch of other meetings that need to take place on a bunch of these items for how we map. about sources, get things implemented as applications and APIs. So we'll book those follow-ups. I think we've got a pretty good breakdown of what needs to be done by the product team and the consortium engineering team, what we're moving towards implementing there. So I guess I'll stop there. If there's any other points or anything that's not clear, but I think this is a great session. We've got a lot of follow-up items.

**Colin Bell** · 52:54

Alright, this is awesome.

**Seth Chalmers** · 52:54

Cool, that's it.

**Kathryn C Vandenberg** · 52:57

Thanks very much, Seth. That was a great. Thank you. Thanks.

**Colin Bell** · 52:57

Hey.

**Adam Love** · 52:58

Awesome.

**Seth Chalmers** · 52:58

Thanks, everyone. Thanks, everyone.

**Robert Chin** · 52:59

Thanks, all. Good conversation. Thanks, Seth. Thanks, everybody.

**Adam Love** · 52:59

Thanks. Thanks.

**Niall Kirk** · 53:04

Thank you.

---

**Source**: `acp-consortium-specs/governance-docs/ACP _-_ Model Risk _-_ GovByDesign Alignment. docx` (Teams transcript, 175 paragraphs).
