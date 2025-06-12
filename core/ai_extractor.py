import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_fields_from_text(text, model="gpt-4o"):
    system_msg = "You are a helpful assistant that extracts structured resume information."

    prompt = f"""
Score this candidate's resume on the following criteria:
1. Technical capabilities are critical in determining whether a candidate can handle the demands of real-world AEC projects. We evaluate their major, degree type, and specific coursework such as AutoCAD, Civil 3D, or HEC-RAS to identify alignment with Arcadis's technical expectations. Additionally, we assess whether the candidate has shown proficiency in tools commonly used in our GBAs like Revit, GIS platforms, or digital data tools like Python or Power BI. We also consider how they describe their project work—do they demonstrate application of these tools in actual problem-solving situations? LinkedIn endorsements, resume skills lists, and cover letter language help supplement our understanding of their technical fluency. Candidates who have hands-on experience, even if academic, signal preparedness and adaptability. We favor those who show initiative in learning industry-standard software, even outside the classroom. Altogether, technical capability scores should reflect both what the candidate knows and how effectively they have demonstrated it. (0–15)
2. Aligned to Arcadis Values:Arcadis values sustainability, integrity, collaboration, and people-first leadership. To evaluate this, we analyze resumes and cover letters for language that mirrors these values. For example, participation in environmental, DEI, or community-focused initiatives can indicate alignment. Involvement in student chapters of SWE, ASCE, EWB, or sustainability-related work is especially relevant. We also consider tone—does the candidate write with purpose, humility, and awareness of global or social challenges? LinkedIn posts or about sections may reveal their professional values and motivations. Candidates who express long-term thinking, curiosity, and commitment to purpose-driven work tend to align well. This score helps us identify who will thrive in a values-driven AEC firm like Arcadis. (0–15)
3. Prior Experience:We assess internships, co-ops, research, and relevant work history for how closely they align to Arcadis's sectors. Candidates with past experience in civil, environmental, water, or mobility engineering settings are ideal. Even if the role wasn't formal, project work or leadership in design competitions can be indicators of potential. Research in sustainability, water management, or transportation analytics adds weight, especially if results were published or presented. Volunteer work that builds teamwork, communication, or leadership should also be credited. We examine both the relevance and the depth of experience—did they simply observe, or were they responsible for deliverables? Titles like 'Engineering Intern' or 'GIS Analyst' often signal better alignment than generic ones. Scoring should reflect a balance between direct experience and transferable skills. (0–10)
4. Resume Quality/Flow: A candidate’s resume is often our first impression of their professionalism. Strong resumes follow a logical structure, avoid grammatical or formatting errors, and clearly communicate accomplishments. We evaluate whether each section is prioritized correctly (e.g., education, experience, skills) and if bullet points use action verbs. Content should highlight outcomes and tools used—not just responsibilities. A cluttered layout or inconsistent formatting may signal a lack of attention to detail. Conversely, clarity and consistency demonstrate effective communication skills, a key requirement at Arcadis. Customizing the resume to the AEC sector—mentioning BIM, stormwater modeling, or climate resilience—shows thoughtfulness. High scores reflect resumes that are clear, tailored, error-free, and impactful. (0–10)
5. Degree Alignment : We score candidates based on whether their degree and major align with typical Arcadis roles in our GBAs. Degrees in Civil, Environmental, Mechanical, Electrical Engineering, or Architecture score highly due to sector demand. We also look for niche degrees that support sustainability, climate planning, or digital transformation. Candidates in Urban Planning, GIS, Environmental Studies, or Water Resources often align well. Double majors or minors in complementary fields are a bonus. We check how their coursework supports their specialization, e.g., hydrology for Water or AutoCAD for Places. Scoring should reward those who clearly fit into Arcadis GBAs or have flexibility across sectors. If the candidate’s degree isn’t a perfect match but their experience is, moderate credit may still be given.(0–20)
6. Geographic Alignment: Geography matters when placing early careers candidates at Arcadis. Candidates who live in, attend school in, or express interest in Arcadis hub cities are more easily deployable. We geotag candidate cities and cross-reference them against offices and hiring zones. LinkedIn location, resume address, and personal statements give strong cues. For example, saying 'looking to work in NYC' and attending NYU is high alignment. We also consider candidates open to relocation or who have ties to multiple cities. If the candidate wants to work in a region where Arcadis has few positions, that reduces their fit slightly. This score helps prioritize placement potential based on real geographic feasibility.(0-15)
7. Academic Achievement: Academic performance signals both preparedness and work ethic. We evaluate GPA in context—3.5+ is ideal, but 3.0+ is often acceptable with other strengths. Rigor of program and reputation of school also matter. We review course content when GPA is low—sometimes a tough load in engineering or GIS explains it. Awards like Dean’s List, scholarships, or honors programs should be noted. We do not penalize candidates for pass/fail semesters during COVID-era disruptions. GPAs in STEM majors carry different weight than in liberal arts. Scoring reflects the balance of GPA, rigor, academic recognition, and context.(0-15)
Given the text below, extract the following details:
- Full Name
- Email Address
- Phone Number
- Latest University
- Degree (e.g., BS, MS)
- Major
- Graduation Date
- Previous University (if any)
- Met on Campus (true/false)
- Campus Scores (based on the criteria above evaluate scores)
- Total Score (Calculate the sum of the above scores)
- Cities/States of interest mentioned

Respond ONLY in valid JSON — no markdown code block, no extra comments.

TEXT:
{text}
"""

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]
    )

    try:
        content = response['choices'][0]['message']['content']
        if content.strip().startswith("```"):
            content = content.strip().strip("`").strip("json").strip()
        return json.loads(content)
    except Exception as e:
        return {"error": str(e), "raw_output": content}
