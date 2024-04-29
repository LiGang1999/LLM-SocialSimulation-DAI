original_prompt = '''Example:
Situation: On November 1, 1986, a fire broke out in the Sandoz AG warehouse located near Schweizerhalle, Basel, Switzerland. During the firefighting process, approximately 10000 cubic meters of firefighting water contaminated with toxic materials flowed into the Rhine River. These sewage flows down the river, and the polluted water in the Rhine River arrived at the French border on the morning of November 1st and the Dutch border on November 9th. The Schweitzehaler fire severely damaged the Rhine River ecosystem and had a negative impact on it for a long time.
Policy: All water plants along the river will be closed and replaced with cars to deliver water to residents. In the Netherlands near Haikou, all river gates connected to the Rhine River are closed. The German government has taken a series of measures to clean and restore the polluted Rhine River, including using technologies such as activated carbon filtration and chemical treatment to purify the river water. In addition, the responsible parties have also been subject to legal sanctions and fines.

Task:
Situation: Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters.
Policy:
'''

spp_prompt = '''When faced with a task, begin by identifying the participants who will contribute to solving the task. Then, initiate a multi-round collaboration process until a final solution is reached. The participants will give critical comments and detailed suggestions whenever necessary.

Here are some examples:
---
Example Task 1: Use numbers and basic arithmetic operations (+ - * /) to obtain 24. You need to use all numbers, and each number can only be used once.
Input: 6 12 1 1

Participants: AI Assistant (you); Math Expert

Start collaboration!

Math Expert: Let's analyze the task in detail. You need to make sure that you meet the requirement, that you need to use exactly the four numbers (6 12 1 1) to construct 24. To reach 24, you can think of the common divisors of 24 such as 4, 6, 8, 3 and try to construct these first. Also you need to think of potential additions that can reach 24, such as 12 + 12.
AI Assistant (you): Thanks for the hints! Here's one initial solution: (12 / (1 + 1)) * 6 = 24
Math Expert: Let's check the answer step by step. (1+1) = 2, (12 / 2) = 6, 6 * 6 = 36 which is not 24! The answer is not correct. Can you fix this by considering other combinations? Please do not make similar mistakes.
AI Assistant (you): Thanks for pointing out the mistake. Here is a revised solution considering 24 can also be reached by 3 * 8: (6 + 1 + 1) * (12 / 4) = 24.
Math Expert: Let's first check if the calculation is correct. (6 + 1 + 1) = 8, 12 / 4 = 3, 8 * 3 = 24. The calculation is correct, but you used 6 1 1 12 4 which is not the same as the input 6 12 1 1. Can you avoid using a number that is not part of the input?
AI Assistant (you): You are right, here is a revised solution considering 24 can be reached by 12 + 12 and without using any additional numbers: 6 * (1 - 1) + 12 = 24.
Math Expert: Let's check the answer again. 1 - 1 = 0, 6 * 0 = 0, 0 + 12 = 12. I believe you are very close, here is a hint: try to change the "1 - 1" to "1 + 1".
AI Assistant (you): Sure, here is the corrected answer:  6 * (1+1) + 12 = 24
Math Expert: Let's verify the solution. 1 + 1 = 2, 6 * 2 = 12, 12 + 12 = 12. You used 1 1 6 12 which is identical to the input 6 12 1 1. Everything looks good!

Finish collaboration!

Final answer: 6 * (1 + 1) + 12 = 24

---
Example Task 2: Write a poem that meets the following requirements: (1) the poem has seven lines and the first letters of each line forms the word "CHATGPT"; (2) the poem is about explaining what is a quantum computer. (3) the poem needs to be easy to understand by a ten years old kid.

Participants: AI Assistant (you); Poet; Computer Scientist; Ten year old child

Poet: Make sure that you write the poem with seven lines, and the first letters of the lines should be C, H, A, T, G, P, T.
Computer Scientist: A quantum computer is an advanced computing device that uses the principles of quantum mechanics to process and store information. Unlike classical computers that use bits to represent information as 0s and 1s, quantum computers use quantum bits or qubits. Qubits can exist in multiple states simultaneously, due to a quantum phenomenon called superposition. You can consider using these information for the poem.
Ten year old child: I hope the poem to be fun and easy to understanding. I don't want to see a lot of jargons or complicated concepts.
AI Assistant (you): Thanks for the guidance! Here's my initial attempt at the poem:
Computational wonder of our age,
Harnessing the quantum world's strange ways,
Atoms dance, entwined in dual state,
Tapping secrets hidden in their haze.

Grand power to solve, simulate,
Profound problems that perplex the wise,
Transforming our future, we await.

Poet: Let's verify if the poem meets the requirements. The first letters are CHATGPT which is correct! And the poem rhymes well. Good job!
Computer Scientist: Everything looks good to me!
Ten year old child: I don't know what does perplex mean. Can you make the use of words easier to understand?
AI Assistant (you): Sure, let me revise the poem by using more common words. Check out the revised version:
Curious machine of our time,
Harnessing the quantum realm's odd ways,
Atoms play, two states they embrace,
Taking secrets from their puzzling maze.

Great power to solve and imitate,
Problems that confuse the brightest minds,
Transforming our future, we await.

Poet: Let's check again if the poem meets the requirements. The first letters are C H A T G P T. And now the poem is more accessible to children. Everything looks good to me.
Computer Scientist: Looking good!
Ten year old child: I like this version a lot!

Finish collaboration!

Final answer:
Curious machine of our time,
Harnessing the quantum realm's odd ways,
Atoms play, two states they embrace,
Taking secrets from their puzzling maze.

Great power to solve and imitate,
Problems that confuse the brightest minds,
Transforming our future, we await.

---
Now, identify the participants and collaboratively solve the following task step by step. Remember to present your final solution with the prefix "Policy:".

Task: Provide policy measures for the following case: {case}
'''

res1 = '''
["Participants: AI Assistant (you); Environmental Expert; Policy Analyst; International Law Expert; Stakeholder Representative\n\nAI Assistant (you): Let's start by analyzing the task in detail. We need to provide policy measures to address the discharge of contaminated water from the Fukushima Daiichi Nuclear Power Plant into the Pacific Ocean. We should consider the potential environmental, legal, and stakeholder implications of our recommendations.\n\nEnvironmental Expert: We need to consider the potential impacts of the contaminated water discharge on marine life, ecosystems, and human health. We should also evaluate the effectiveness of different treatment methods to reduce the radioactive levels in the water before discharge.\n\nPolicy Analyst: We should consider the regulatory framework and international agreements related to nuclear safety and environmental protection. We should also assess the political and economic feasibility of different policy measures.\n\nInternational Law Expert: We should consider the international laws and treaties related to marine pollution and the rights and responsibilities of different stakeholders involved.\n\nStakeholder Representative: We should consider the perspectives and concerns of different stakeholders, including local communities, fishermen, and industries affected by the discharge.\n\nAI Assistant (you): Based on the input from the experts, here are some initial policy measures to address the discharge of contaminated water from the Fukushima Daiichi Nuclear Power Plant into the Pacific Ocean:\n\n1. Implement strict regulations and standards for the treatment of contaminated water to ensure that the radioactive levels are reduced to safe levels before discharge.\n2. Conduct regular monitoring and assessment of the impacts of the contaminated water discharge on marine life, ecosystems, and human health.\n3. Engage with international organizations and treaties related to nuclear safety and environmental protection to coordinate efforts and share best practices.\n4. Involve local communities, fishermen, and industries in the decision-making process and provide them with accurate and timely information about the discharge.\n5. Develop and implement emergency response plans in case of any accidents or incidents related to the discharge.\n\nEnvironmental Expert: Let's check if the policy measures are feasible and effective. The measures address the potential impacts of the discharge and the need for monitoring and assessment. However, we should also consider the long-term impacts and the need for more effective treatment methods.\n\nPolicy Analyst: Let's evaluate the political and economic feasibility of the policy measures. The measures are feasible from a regulatory perspective, but we should also consider the economic costs and benefits of different treatment methods and the potential impacts on the nuclear industry.\n\nInternational Law Expert: Let's consider the international laws and treaties related to marine pollution and the rights and responsibilities of different stakeholders involved. The measures should be consistent with international law and should respect the rights and responsibilities of different stakeholders.\n\nStakeholder Representative: Let's consider the perspectives and concerns of different stakeholders. The measures should address their concerns and involve them in the decision-making process.\n\nAI Assistant (you): Based on the feedback from the experts, here is a revised set of policy measures to address the discharge of contaminated water from the Fukushima Daiichi Nuclear Power Plant into the Pacific Ocean:\n\n1. Implement strict regulations and standards for the treatment of contaminated water to ensure that the radioactive levels are reduced to safe levels before discharge.\n2. Conduct regular monitoring and assessment of the impacts of the contaminated water discharge on marine life, ecosystems, and human health.\n3. Engage with international organizations and treaties related to nuclear safety and environmental protection to coordinate efforts and share best practices.\n4. Involve local communities, fishermen, and industries in the decision-making process and provide them with accurate and timely information about the discharge.\n5. Develop and implement emergency response plans in case of any accidents or incidents related to the discharge.\n6. Invest in research and development of more effective treatment methods to reduce the radioactive levels in the water before discharge.\n7. Consider the economic costs and benefits of different treatment methods and the potential impacts on the nuclear industry, and ensure that the measures are consistent with international law and respect the rights and responsibilities of different stakeholders.\n\nEnvironmental Expert: Let's verify if the policy measures are comprehensive and effective. The measures address the potential impacts of the discharge, the need for monitoring and assessment, and the need for more effective treatment methods. Everything looks good!\n\nPolicy Analyst: Let's evaluate the political and economic feasibility of the policy measures. The measures are feasible from a regulatory and economic perspective, and they consider the potential impacts on the nuclear industry.\n\nInternational Law Expert: Let's ensure that the policy measures are consistent with international law and respect the rights and responsibilities of different stakeholders. The measures address the legal and regulatory aspects of the discharge.\n\nStakeholder Representative: Let's ensure that the policy measures address the concerns and perspectives of different stakeholders. The measures involve them in the decision-making process and provide them with accurate and timely information.\n\nAI Assistant (you): Based on the feedback from the experts, here is the final set of policy measures to address the discharge of contaminated water from the Fukushima Daiichi Nuclear Power Plant into the Pacific Ocean:\n\nPolicy: Implement strict regulations and standards for the treatment of contaminated water to ensure that the radioactive levels are reduced to safe levels before discharge. Conduct regular monitoring and assessment of the impacts of the contaminated water discharge on marine life, ecosystems, and human health. Engage with international organizations and treaties related to nuclear safety and environmental protection to coordinate efforts and share best practices. Involve local communities, fishermen, and industries in the decision-making process and provide them with accurate and timely information about the discharge. Develop and implement emergency response plans in case of any accidents or incidents related to the discharge. Invest in research and development of more effective treatment methods to reduce the radioactive levels in the water before discharge. Consider the economic costs and benefits of different treatment methods and the potential impacts on the nuclear industry, and ensure that the measures are consistent with international law and respect the rights and responsibilities of different stakeholders."]
'''

res2 = '''
['Implement strict regulations and standards for the treatment of contaminated water to ensure that the radioactive levels are reduced to safe levels before discharge. Conduct regular monitoring and assessment of the impacts of the contaminated water discharge on marine life, ecosystems, and human health. Engage with international organizations and treaties related to nuclear safety and environmental protection to coordinate efforts and share best practices. Involve local communities, fishermen, and industries in the decision-making process and provide them with accurate and timely information about the discharge. Develop and implement emergency response plans in case of any accidents or incidents related to the discharge. Invest in research and development of more effective treatment methods to reduce the radioactive levels in the water before discharge. Consider the economic costs and benefits of different treatment methods and the potential impacts on the nuclear industry, and ensure that the measures are consistent with international law and respect the rights and responsibilities of different stakeholders.']
'''
