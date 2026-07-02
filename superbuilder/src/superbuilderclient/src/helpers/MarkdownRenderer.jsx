import React from "react";
import ReactMarkdown from "react-markdown";
import { openUrl } from "@tauri-apps/plugin-opener";

function addLineBreaksToMarkdown(markdown) {
  // Regular expression to match Markdown headers
  const headerRegex = /(?<=\s)(#{1,6}\s)/g;
  // Replace occurrences of headers with a line break followed by the header
  return markdown.replace(headerRegex, "\n$1");
}

const MarkdownRenderer = ({ content, id }) => {
  const formattedMarkdown = addLineBreaksToMarkdown(content);
  return (
    <div className="notes-text">
      <ReactMarkdown
        components={{
          a: ({ href, children, ...props }) => (
            <a
              {...props}
              href={href}
              onClick={(e) => {
                e.preventDefault(); // Prevent default navigation
                openUrl(href); // Open in system browser
              }}
              style={{
                color: "blue",
                textDecoration: "underline",
                cursor: "pointer",
              }}
            >
              {children}
            </a>
          ),
        }}
      >
        {formattedMarkdown}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
