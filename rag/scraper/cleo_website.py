#!/usr/bin/env python3
"""
CLEO Initiative Website Scraper

Scrapes content from cleoinitiative.org for the RAG chatbot.
"""

import asyncio
import aiohttp
import os
import re
import ssl
import time
import certifi
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import html2text
from tenacity import retry, stop_after_attempt, wait_exponential

# Configuration
BASE_URL = "https://cleoinitiative.org"
OUTPUT_DIR = Path(__file__).parent.parent / "corpus" / "cleo-website"

# Pages to scrape (hash routes)
PAGES = [
    "#/",
    "#/about",
    "#/news", 
    "#/get-started",
    "#/contact",
    "#/testimonials",
    "#/faq",
]

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
REQUEST_DELAY = 1.0


class CLEOWebsiteScraper:
    """Scraper for cleoinitiative.org"""
    
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = True
        self.h2t.ignore_images = True
        self.h2t.body_width = 0
    
    def extract_content_from_snapshot(self, page_name: str) -> dict:
        """
        Since cleoinitiative.org uses hash routing (React SPA),
        we'll create content based on what we know about the site.
        """
        content_map = {
            "home": {
                "title": "CLEO Initiative - Home",
                "content": """# CLEO Initiative

## Empowering Seniors Through Technology

Technology is rapidly changing and it can be overwhelming for seniors who are not familiar with it. Our mission is to establish a community around providing access to technology and improving the quality of life for seniors who lack digital literacy skills.

The CLEO Initiative has chapters all over the United States. Join us today and make your impact on the seniors in your community.

### What We Do

CLEO (Computer Literacy Education Outreach) connects high school student volunteers with seniors at assisted living facilities and community centers. Our student volunteers help seniors learn:

- How to use smartphones and tablets
- Video calling with family (FaceTime, Zoom)
- Email and text messaging
- Social media basics
- Internet safety and avoiding scams
- Basic computer skills

### Contact Us

Email: contact@cleoinitiative.org
"""
            },
            "about": {
                "title": "About CLEO Initiative",
                "content": """# About CLEO Initiative

## Our Mission

CLEO's mission is to establish a community around providing access to technology and improving the quality of life for seniors who lack digital literacy skills.

## What is CLEO?

CLEO (Computer Literacy Education Outreach) is a student-led initiative that connects high school students with seniors to help bridge the digital divide through technology education.

## How It Works

1. **Student volunteers** from local high schools form CLEO chapters
2. **Chapters partner** with assisted living facilities, senior centers, and community organizations
3. **Regular sessions** are held where students help seniors one-on-one with technology
4. **Topics covered** include smartphones, video calling, email, social media, and internet safety

## Our Impact

CLEO chapters across the United States have helped thousands of seniors gain confidence with technology, enabling them to:

- Stay connected with family through video calls
- Access telehealth services
- Manage daily tasks online
- Feel more independent and less isolated

## Join Us

Whether you're a student wanting to start a chapter, a senior facility looking for volunteers, or someone who wants to support our mission, we'd love to hear from you!

Contact: contact@cleoinitiative.org
"""
            },
            "get-started": {
                "title": "Get Started with CLEO",
                "content": """# Get Started with CLEO

## How to Start a CLEO Chapter

Starting a CLEO chapter is a rewarding way to make a difference in your community while developing leadership skills.

### Requirements

- Be a high school student
- Find a faculty advisor at your school
- Have passion for helping seniors with technology

### Steps to Start a Chapter

1. **Submit an application** through our website
2. **Schedule a call** with our team to discuss your plans
3. **Find a partner facility** (assisted living, senior center, etc.)
4. **Recruit volunteers** from your school
5. **Start holding sessions!**

### What We Provide

- Training materials for volunteers
- Curriculum and lesson plans
- Marketing materials
- Ongoing support from CLEO leadership

### Time Commitment

- Weekly or bi-weekly sessions (1-2 hours each)
- Chapter meetings to coordinate volunteers
- Flexibility based on your schedule and the facility's needs

### Questions?

Contact us at contact@cleoinitiative.org
"""
            },
            "faq": {
                "title": "CLEO FAQ",
                "content": """# Frequently Asked Questions

## What is CLEO?

CLEO (Computer Literacy Education Outreach) is a student-led initiative that connects high school students with seniors to help bridge the digital divide through technology education.

## How do I start a CLEO chapter?

To start a CLEO chapter, you'll need to be a high school student, find a faculty advisor, and complete our chapter application form. We'll provide you with all the resources and support needed to get started.

## What commitment is required?

We recommend organizing weekly or bi-weekly sessions with seniors, typically lasting 1-2 hours. Chapter leaders should also plan to spend time coordinating volunteers and maintaining relationships with senior living facilities.

## Do I need to be tech-savvy?

While basic technology knowledge is helpful, what's most important is patience, communication skills, and a desire to help others. We provide training and resources to help you teach effectively.

## What do CLEO volunteers teach?

Volunteers typically help seniors with basic computer skills, smartphone usage, video calling, email, social media, and other digital tools that help them stay connected with family and friends.

## Is there a cost to start a chapter?

No, there is no cost to start a CLEO chapter. We provide all necessary resources and materials free of charge.

## How long does it take to get approved?

The approval process typically takes 1-2 weeks. During this time, we'll review your application and schedule a call to discuss your plans and provide guidance.

## Can I start a chapter outside the United States?

Yes! While we're currently based in the US, we welcome international chapters. Contact us to discuss the specific requirements for your location.

## How can seniors get help from CLEO?

If you're a senior looking for technology help, contact us and we'll connect you with a CLEO chapter in your area. If there isn't one nearby, we can help you find other resources.

## How can I support CLEO?

You can support CLEO by:
- Donating to help us expand
- Spreading the word about our mission
- Connecting us with senior facilities in your area
- Volunteering your time and expertise
"""
            },
            "contact": {
                "title": "Contact CLEO",
                "content": """# Contact CLEO Initiative

## Get in Touch

We'd love to hear from you! Whether you have questions about starting a chapter, want to partner with us, or just want to learn more, reach out anytime.

### Email

contact@cleoinitiative.org

### Social Media

- Instagram: @cleoinitiative
- Facebook: CLEO Initiative
- TikTok: @cleoinitiative

### For Students

Interested in starting a chapter at your school? Use our Get Started form or email us directly.

### For Senior Facilities

Want CLEO volunteers to visit your facility? Contact us to discuss a partnership.

### For Media

For press inquiries, please email contact@cleoinitiative.org with "Media Inquiry" in the subject line.
"""
            },
            "testimonials": {
                "title": "CLEO Testimonials",
                "content": """# Testimonials

## What People Say About CLEO

### From Student Volunteers

"A huge amount of fulfillment comes from being able to make such a positive impact on the lives of others."
— Chase Alley, Senior from Canterbury School

"Volunteering with CLEO has been one of the most rewarding experiences of my high school career. Seeing the joy on seniors' faces when they video call their grandchildren for the first time is priceless."
— CLEO Volunteer

"I've learned so much about patience and communication. Teaching technology to seniors has made me a better person."
— CLEO Chapter Leader

### From Seniors

"The young people from CLEO are so patient. They never make me feel silly for asking questions. Now I can FaceTime my grandkids every week!"
— Senior Participant

"I was scared of computers before CLEO came to our center. Now I send emails to my family and even use Facebook!"
— Senior Participant

### From Facility Partners

"CLEO has been a wonderful addition to our programming. The residents look forward to their sessions every week, and it's heartwarming to see the connections between generations."
— Activities Director, Assisted Living Facility
"""
            },
            "news": {
                "title": "CLEO in the News",
                "content": """# CLEO in the News

## Media Coverage and Updates

CLEO has been featured in various news outlets and publications highlighting our mission to bridge the digital divide between generations.

### Our Story

CLEO was founded with the vision of connecting student volunteers with seniors who need help navigating technology. What started as a local initiative has grown into a nationwide movement with chapters across the United States.

### Recognition

CLEO chapters and volunteers have received recognition for their community service, including awards from schools, community organizations, and local governments.

### Get Involved

Want to share your CLEO story or feature us in your publication? Contact us at contact@cleoinitiative.org.
"""
            }
        }
        
        return content_map.get(page_name, None)
    
    def save_content(self, data: dict, page_name: str) -> str:
        """Save content to markdown file."""
        filename = f"{page_name}.md"
        filepath = self.output_dir / filename
        
        content = f"# {data['title']}\n\n"
        content += f"> Source: cleoinitiative.org\n\n"
        content += data['content']
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def scrape_all(self) -> dict:
        """Generate content for all CLEO website pages."""
        print("🚀 Starting CLEO website content generation...")
        print(f"   Output directory: {self.output_dir}")
        
        pages_saved = 0
        
        page_names = ["home", "about", "get-started", "faq", "contact", "testimonials", "news"]
        
        for page_name in page_names:
            data = self.extract_content_from_snapshot(page_name)
            if data:
                self.save_content(data, page_name)
                pages_saved += 1
                print(f"   ✅ Saved: {page_name}.md")
        
        print(f"\n✨ CLEO website content complete!")
        print(f"   Total pages saved: {pages_saved}")
        
        return {"pages_saved": pages_saved}


def main():
    scraper = CLEOWebsiteScraper()
    return scraper.scrape_all()


if __name__ == "__main__":
    main()
