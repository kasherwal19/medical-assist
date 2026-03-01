"""
Template formatting mixin for chat service.
Handles HTML template formatting and markdown conversion.
"""

import json
import markdown
from typing import List
from lib.logger import logging
from services.llm_service import brain
from utils.prompt import TEMPLATE_FORMATTING_PROMPT
from utils.template import templates
from .utils import clean_text


class TemplateMixin:
    """Mixin class for template formatting methods."""

    async def format_content_with_ai(self, template_id: str, content: str, images: List[str] = [], query: str = "") -> str:
        """
        Use AI to format markdown into structured HTML for templates.
        """
        try:
            if template_id not in templates:
                logging.warning(f"Template {template_id} not found, using template 1")
                template_id = "1"

            formatting_prompt = TEMPLATE_FORMATTING_PROMPT.format(
                template_id=template_id,
                content=content,
                images=images if images else [""],
                query=query
            )

            response = await brain.call_invoke(prompt=formatting_prompt)

            try:
                response_text = response.content.strip()
                if response_text.startswith("```"):
                    response_text = response_text.replace("```json", "").replace("```", "").strip()

                formatted_data = json.loads(response_text)

            except json.JSONDecodeError:
                logging.error("AI response is not valid JSON. Falling back.")
                return await self.format_with_template(template_id, content, images, query)

            template_str = templates[template_id]

            if template_id in ["1", "hero"]:
                image_url = images[0] if images else ""
                template_str = template_str.replace("{image_url}", image_url)
                template_str = template_str.replace("{content}", formatted_data.get("content", ""))

            elif template_id in ["2", "dual"]:
                template_str = template_str.replace("{image_url_1}", images[0] if len(images) > 0 else "")
                template_str = template_str.replace("{image_url_2}", images[1] if len(images) > 1 else "")
                template_str = template_str.replace("{content_1}", formatted_data.get("content_1", ""))
                template_str = template_str.replace("{content_2}", formatted_data.get("content_2", ""))

            elif template_id in ["3", "embedded"]:
                template_str = template_str.replace("{title}", formatted_data.get("title", ""))
                template_str = template_str.replace("{image_url}", images[0] if images else "")
                template_str = template_str.replace("{side_content}", formatted_data.get("side_content", ""))
                template_str = template_str.replace("{below_content}", formatted_data.get("below_content", ""))

            elif template_id in ["4", "plainhero"]:
                template_str = template_str.replace("{content}", formatted_data.get("content", ""))

            elif template_id in ["5", "plaindual"]:
                template_str = template_str.replace("{content_1}", formatted_data.get("content_1", ""))
                template_str = template_str.replace("{content_2}", formatted_data.get("content_2", ""))

        
            return template_str

        except Exception as e:
            logging.error(f"AI template formatting failed: {str(e)}", exc_info=True)
            return await self.format_with_template(template_id, content, images, query)

    def markdown_to_html(self, markdown_text: str) -> str:
        """Convert Markdown to HTML using markdown library."""
        try:
            return markdown.markdown(
                markdown_text,
                extensions=["extra", "nl2br", "sane_lists"]
            )
        except Exception as e:
            logging.error(f"Markdown conversion failed: {e}")
            return markdown_text

    async def format_markdown_to_template(self, template_id: str, content: str, images: List[str] = None, query: str = "") -> str:
        """Format Markdown content into HTML template without LLM call."""
        if images is None:
            images = []

        try:
            template_map = {
                "1": "hero", "hero": "hero",
                "2": "dual", "dual": "dual",
                "3": "embedded", "embedded": "embedded",
                "4": "plainhero", "plainhero": "plainhero",
                "5": "plaindual", "plaindual": "plaindual",
            }
            template_id = template_map.get(template_id, "plainhero")

            if template_id not in templates:
                template_id = "plainhero"

            template_str = templates[template_id]
            html_content = self.markdown_to_html(content)

            if template_id == "hero":
                return template_str.replace("{image_url}", images[0] if images else "").replace("{content}", html_content)

            if template_id == "dual":
                mid = len(html_content) // 2
                split_point = html_content.rfind("</p>", 0, mid + 100)
                if split_point == -1:
                    split_point = mid
                else:
                    split_point += 4
                return (
                    template_str
                    .replace("{image_url_1}", images[0] if len(images) > 0 else "")
                    .replace("{image_url_2}", images[1] if len(images) > 1 else "")
                    .replace("{content_1}", html_content[:split_point])
                    .replace("{content_2}", html_content[split_point:])
                )

            if template_id == "embedded":
                title = query[:100] if query else "Clinical Summary"
                split_point = int(len(html_content) * 0.3)
                paragraph_split = html_content.rfind("</p>", 0, split_point + 50)
                if paragraph_split != -1:
                    split_point = paragraph_split + 4
                return (
                    template_str
                    .replace("{title}", title)
                    .replace("{image_url}", images[0] if images else "")
                    .replace("{side_content}", html_content[:split_point])
                    .replace("{below_content}", html_content[split_point:])
                )

            if template_id == "plainhero":
                return template_str.replace("{content}", html_content)

            if template_id == "plaindual":
                mid = len(html_content) // 2
                split_point = html_content.rfind("</p>", 0, mid + 100)
                if split_point == -1:
                    split_point = mid
                else:
                    split_point += 4
                return (
                    template_str
                    .replace("{content_1}", html_content[:split_point])
                    .replace("{content_2}", html_content[split_point:])
                )

            return html_content

        except Exception as e:
            logging.error(f"Template formatting failed: {e}", exc_info=True)
            return content
    
    
    async def format_with_template(self, template_id: str, content: str, images: List[str] = [], query: str = "") -> str:
        """
        Fallback method for template formatting.
        """
        try:
            if template_id not in templates:
                template_id = "1"

            template_str = templates[template_id]
            cleaned_content = clean_text(content)

            if template_id in ["1", "hero"]:
                return template_str.replace("{image_url}", images[0] if images else "").replace("{content}", cleaned_content)

            elif template_id in ["2", "dual"]:
                mid = len(cleaned_content) // 2
                return (
                    template_str
                    .replace("{image_url_1}", images[0] if len(images) > 0 else "")
                    .replace("{image_url_2}", images[1] if len(images) > 1 else "")
                    .replace("{content_1}", cleaned_content[:mid])
                    .replace("{content_2}", cleaned_content[mid:])
                )

            elif template_id in ["3", "embedded"]:
                title = query[:100] if query else "Generated Content"
                mid = int(len(cleaned_content) * 0.3)
                return (
                    template_str
                    .replace("{title}", title)
                    .replace("{image_url}", images[0] if images else "")
                    .replace("{side_content}", cleaned_content[:mid])
                    .replace("{below_content}", cleaned_content[mid:])
                )

            elif template_id in ["4", "plainhero"]:
                return template_str.replace("{content}", cleaned_content)

            elif template_id in ["5", "plaindual"]:
                mid = len(cleaned_content) // 2
                return (
                    template_str
                    .replace("{content_1}", cleaned_content[:mid])
                    .replace("{content_2}", cleaned_content[mid:])
                )
            
            return content

        except Exception as e:
            logging.error(f"Template formatting failed: {str(e)}", exc_info=True)
            return content
