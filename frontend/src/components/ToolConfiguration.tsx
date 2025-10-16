import { useState } from "react";

interface ToolConfigurationProps {
  selectedTools: string[];
  onChange: (tools: string[]) => void;
}

interface Tool {
  id: string;
  name: string;
  description: string;
  category: string;
}

const AVAILABLE_TOOLS: Tool[] = [
  {
    id: "web_search",
    name: "Web Search",
    description: "Search the web for information",
    category: "Information",
  },
  {
    id: "code_execution",
    name: "Code Execution",
    description: "Execute Python code",
    category: "Development",
  },
  {
    id: "file_operations",
    name: "File Operations",
    description: "Read and write files",
    category: "System",
  },
  {
    id: "data_analysis",
    name: "Data Analysis",
    description: "Analyze data and generate insights",
    category: "Analytics",
  },
  {
    id: "image_generation",
    name: "Image Generation",
    description: "Generate images from text",
    category: "Media",
  },
];

export function ToolConfiguration({
  selectedTools,
  onChange,
}: ToolConfigurationProps): JSX.Element {
  const [searchTerm, setSearchTerm] = useState("");

  const handleToggleTool = (toolId: string) => {
    if (selectedTools.includes(toolId)) {
      onChange(selectedTools.filter((id) => id !== toolId));
    } else {
      onChange([...selectedTools, toolId]);
    }
  };

  const filteredTools = AVAILABLE_TOOLS.filter(
    (tool) =>
      tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tool.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const groupedTools = filteredTools.reduce(
    (acc, tool) => {
      if (!acc[tool.category]) {
        acc[tool.category] = [];
      }
      acc[tool.category].push(tool);
      return acc;
    },
    {} as Record<string, Tool[]>
  );

  return (
    <div className="tool-configuration">
      <div className="tool-configuration__header">
        <input
          type="text"
          className="tool-configuration__search"
          placeholder="Search tools..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <span className="tool-configuration__count">
          {selectedTools.length} tool{selectedTools.length !== 1 ? "s" : ""} selected
        </span>
      </div>

      <div className="tool-configuration__list">
        {Object.entries(groupedTools).map(([category, tools]) => (
          <div key={category} className="tool-configuration__category">
            <h3 className="tool-configuration__category-title">{category}</h3>
            <div className="tool-configuration__tools">
              {tools.map((tool) => (
                <label key={tool.id} className="tool-card">
                  <input
                    type="checkbox"
                    checked={selectedTools.includes(tool.id)}
                    onChange={() => handleToggleTool(tool.id)}
                  />
                  <div className="tool-card__content">
                    <div className="tool-card__name">{tool.name}</div>
                    <div className="tool-card__description">{tool.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      {selectedTools.length > 0 && (
        <div className="tool-configuration__selected">
          <h4>Selected Tools:</h4>
          <div className="tool-configuration__tags">
            {selectedTools.map((toolId) => {
              const tool = AVAILABLE_TOOLS.find((t) => t.id === toolId);
              return (
                <span key={toolId} className="tool-tag">
                  {tool?.name}
                  <button
                    type="button"
                    className="tool-tag__remove"
                    onClick={() => handleToggleTool(toolId)}
                    aria-label={`Remove ${tool?.name}`}
                  >
                    ×
                  </button>
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

