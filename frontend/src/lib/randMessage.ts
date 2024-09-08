import { ChatMessage } from "@/SimContext";
import { apis } from "./api";

const generateDemoMessages = (persona: apis.Agent): ChatMessage[] => {
    const messageCount = Math.floor(Math.random() * 5) + 3; // Random number of messages between 3 and 7
    const messages: ChatMessage[] = [];

    messages.push({
        sender: persona.name,
        content: getRandomGreeting(persona),
        timestamp: new Date(Date.now() - 1000000).toLocaleTimeString(),
        type: 'private',
        role: 'agent',
        subject: 'Greeting'
    });

    for (let i = 1; i < messageCount; i++) {
        const isUserMessage = i % 2 === 1;
        const topic = getRandomTopic();

        messages.push({
            sender: isUserMessage ? 'user' : persona.name,
            content: isUserMessage ? getUserQuestion(topic) : getAgentResponse(persona, topic),
            timestamp: new Date(Date.now() - (messageCount - i) * 100000).toLocaleTimeString(),
            type: 'private',
            role: isUserMessage ? 'user' : 'agent',
            subject: isUserMessage ? `Question about ${topic}` : `Discussing ${topic}`
        });
    }

    return messages;
};

const getRandomTopic = (): string => {
    const topics = ['work', 'hobbies', 'goals', 'challenges', 'achievements', 'skills', 'future', 'collaboration'];
    return topics[Math.floor(Math.random() * topics.length)];
};

const getRandomGreeting = (persona: apis.Agent): string => {
    const greetings = [
        `Hello there! I'm ${persona.first_name}. It's a pleasure to meet you!`,
        `Hi! ${persona.first_name} here. How can I brighten your day?`,
        `Greetings! I'm ${persona.first_name}. I'm excited to chat with you!`,
        `Good day! ${persona.first_name} at your service. What shall we discuss?`,
        `Hey! It's ${persona.first_name}. Ready for an interesting conversation?`
    ];
    return greetings[Math.floor(Math.random() * greetings.length)];
};

const getUserQuestion = (topic: string): string => {
    const questions: Record<string, string[]> = {
        work: [
            "What's the most interesting project you're working on right now?",
            "How do you approach problem-solving in your work?",
            "What's a typical day like in your current role?"
        ],
        hobbies: [
            "Do you have any unique hobbies or interests you'd like to share?",
            "How do your hobbies influence your professional life?",
            "What's a skill you've picked up from your hobbies?"
        ],
        goals: [
            "What's a big goal you're currently working towards?",
            "How do you set and track your professional goals?",
            "Where do you see yourself in the next few years?"
        ],
        challenges: [
            "What's a challenge you're facing and how are you tackling it?",
            "How do you stay motivated when facing obstacles?",
            "Can you share a difficult decision you had to make recently?"
        ],
        achievements: [
            "What's a recent achievement you're proud of?",
            "How do you celebrate your successes?",
            "What's been your most significant professional milestone so far?"
        ],
        skills: [
            "What new skill are you currently learning or improving?",
            "How do you keep your skills up-to-date in your field?",
            "What skill do you think will be crucial in your industry's future?"
        ],
        future: [
            "How do you think your field will evolve in the coming years?",
            "What future trends are you excited about in your industry?",
            "How are you preparing for future changes in your profession?"
        ],
        collaboration: [
            "How do you approach collaboration with team members?",
            "What's your experience with cross-functional projects?",
            "How do you handle disagreements in a professional setting?"
        ]
    };
    const topicQuestions = questions[topic] || questions['work'];
    return topicQuestions[Math.floor(Math.random() * topicQuestions.length)];
};

const getAgentResponse = (persona: apis.Agent, topic: string): string => {
    const responses: Record<string, string[]> = {
        work: [
            `Currently, I'm deeply involved in ${persona.currently}. It's challenging but incredibly rewarding. I'm applying my ${persona.learned} skills to push the boundaries of what's possible in this field.`,
            `My work on ${persona.currently} is at an exciting stage. I'm leveraging my background in ${persona.innate} to bring a unique perspective to the project.`,
            `In my current role, I'm focusing on ${persona.currently}. It's fascinating how my ${persona.learned} skills are proving crucial in tackling complex problems.`
        ],
        hobbies: [
            `One of my passions is exploring ${persona.innate}. It's fascinating how it relates to my work in ${persona.currently}. In my free time, I also enjoy ${persona.lifestyle}, which helps me maintain a good work-life balance.`,
            `I'm quite enthusiastic about ${persona.innate}. It's a great way to unwind from my work on ${persona.currently} and often provides unexpected insights.`,
            `${persona.lifestyle} is a big part of my life outside work. It's amazing how it complements my professional focus on ${persona.currently} and enhances my creativity.`
        ],
        goals: [
            `My main goal right now is to excel in ${persona.currently}. I'm also aiming to further develop my ${persona.learned} skills. Long-term, I aspire to make a significant impact in the field of ${persona.innate}.`,
            `I'm working towards becoming a thought leader in ${persona.currently}. This involves not only honing my ${persona.learned} skills but also deepening my understanding of ${persona.innate}.`,
            `A key goal for me is to innovate in the intersection of ${persona.currently} and ${persona.innate}. I believe this unique combination could lead to groundbreaking developments.`
        ],
        challenges: [
            `A major challenge I'm facing is balancing my work on ${persona.currently} with my desire to improve in ${persona.learned}. I'm tackling this by setting clear priorities and seeking mentorship from experts in both areas.`,
            `The rapid evolution of ${persona.currently} presents a constant challenge. I'm addressing this by dedicating time to continuous learning, particularly in ${persona.learned}.`,
            `Integrating ${persona.innate} principles into ${persona.currently} is challenging but exciting. I'm overcoming this by collaborating with experts from diverse backgrounds.`
        ],
        achievements: [
            `Recently, I made a breakthrough in ${persona.currently} by applying my knowledge of ${persona.innate} in an innovative way. It's been recognized within my field, and I'm excited to build upon this success.`,
            `I'm proud of successfully implementing a new approach to ${persona.currently} that draws on my ${persona.learned} skills. It's significantly improved our team's efficiency.`,
            `A recent highlight was presenting my work on ${persona.currently} at a major conference. The positive reception has opened up new collaborative opportunities.`
        ],
        skills: [
            `I'm currently enhancing my proficiency in ${persona.learned}, which is becoming increasingly relevant to my work in ${persona.currently}.`,
            `Staying updated with the latest developments in ${persona.currently} is crucial. I'm also exploring how to better integrate my knowledge of ${persona.innate} into my daily work.`,
            `I believe that combining ${persona.learned} with a deep understanding of ${persona.innate} will be a game-changer in our field. That's why I'm focusing on developing this unique skill set.`
        ],
        future: [
            `I see ${persona.currently} evolving to incorporate more elements of ${persona.innate}. I'm positioning myself at the forefront of this trend by deepening my expertise in both areas.`,
            `The future of our field lies in the integration of ${persona.currently} with advanced ${persona.learned} techniques. I'm excited to be part of this transformation.`,
            `I anticipate a shift towards more ${persona.lifestyle}-oriented approaches in ${persona.currently}. This aligns perfectly with my background and interests.`
        ],
        collaboration: [
            `In collaborative projects, I bring my expertise in ${persona.currently} to the table while always being open to insights from colleagues with different backgrounds, especially in ${persona.innate}.`,
            `I find that my background in ${persona.innate} often provides a unique perspective in team discussions about ${persona.currently}. It helps bridge gaps and foster innovative solutions.`,
            `When collaborating, I emphasize the importance of integrating diverse skills. My experience with both ${persona.currently} and ${persona.learned} has shown me the value of multidisciplinary approaches.`
        ]
    };
    const topicResponses = responses[topic] || responses['work'];
    return topicResponses[Math.floor(Math.random() * topicResponses.length)];
};