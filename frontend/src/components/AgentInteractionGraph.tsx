import type { InteractionGraph } from "../api/types";

interface AgentInteractionGraphProps {
  graph: InteractionGraph | null;
  isLoading: boolean;
  error: string | null;
  onRefresh?: () => void;
}

const CANVAS_WIDTH = 960;
const CANVAS_HEIGHT = 560;

const NODE_CLASS_BY_TYPE: Record<string, string> = {
  agent: "graph-node graph-node--agent",
  user: "graph-node graph-node--user",
  system: "graph-node graph-node--system",
  unknown: "graph-node graph-node--unknown",
};

function renderLoadingState(): JSX.Element {
  return <div className="graph-panel__placeholder">Loading interaction data...</div>;
}

function renderEmptyState(): JSX.Element {
  return (
    <div className="graph-panel__placeholder">
      Select a group chat and run a conversation to visualize agent interactions.
    </div>
  );
}

function GraphLegend(): JSX.Element {
  return (
    <dl className="graph-legend">
      <div>
        <dt className="graph-legend__marker graph-legend__marker--agent" />
        <dd>Agent (AutoGen participant)</dd>
      </div>
      <div>
        <dt className="graph-legend__marker graph-legend__marker--user" />
        <dd>User initiated message</dd>
      </div>
      <div>
        <dt className="graph-legend__marker graph-legend__marker--system" />
        <dd>System orchestration event</dd>
      </div>
      <div>
        <dt className="graph-legend__marker graph-legend__marker--unknown" />
        <dd>Unclassified sender</dd>
      </div>
    </dl>
  );
}

export function AgentInteractionGraph(
  props: AgentInteractionGraphProps,
): JSX.Element {
  const { graph, isLoading, error, onRefresh } = props;

  if (error) {
    return (
      <div className="graph-panel">
        <div className="graph-panel__header">
          <h2>Agent Interaction Graph</h2>
          {onRefresh ? (
            <button className="button button--ghost" type="button" onClick={onRefresh}>
              Retry
            </button>
          ) : null}
        </div>
        <div className="graph-panel__placeholder graph-panel__placeholder--error">
          {error}
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="graph-panel">
        <div className="graph-panel__header">
          <h2>Agent Interaction Graph</h2>
        </div>
        {renderLoadingState()}
      </div>
    );
  }

  return (
    <div className="graph-panel">
      <div className="graph-panel__header">
        <h2>Agent Interaction Graph</h2>
        {onRefresh ? (
          <button className="button button--ghost" type="button" onClick={onRefresh}>
            Refresh
          </button>
        ) : null}
      </div>
      <div className="graph-panel__canvas">
        {graph ? renderGraphSvg(graph) : renderEmptyState()}
      </div>
      <GraphLegend />
    </div>
  );
}

function renderGraphSvg(graph: InteractionGraph): JSX.Element {
  const nodeById = new Map(graph.nodes.map((node) => [node.id, node]));
  const maxEdgeCount = graph.edges.reduce((max, edge) => Math.max(max, edge.count), 1);

  return (
    <svg
      className="graph-canvas"
      viewBox={`0 0 ${CANVAS_WIDTH} ${CANVAS_HEIGHT}`}
      role="img"
      aria-label="Agent interaction graph"
    >
      <defs>
        <marker
          id="edge-arrow"
          viewBox="0 0 10 10"
          refX="10"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
          className="graph-edge__arrow"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" />
        </marker>
      </defs>

      {graph.edges.map((edge) => {
        const source = nodeById.get(edge.source);
        const target = nodeById.get(edge.target);
        if (!source || !target) {
          return null;
        }

        const strokeWidth = 1.5 + (edge.count / maxEdgeCount) * 4;
        const midX = (source.position.x + target.position.x) / 2;
        const midY = (source.position.y + target.position.y) / 2;

        return (
          <g key={edge.id} className="graph-edge">
            <line
              x1={source.position.x}
              y1={source.position.y}
              x2={target.position.x}
              y2={target.position.y}
              strokeWidth={strokeWidth}
              markerEnd="url(#edge-arrow)"
            />
            <text x={midX} y={midY - 6} className="graph-edge__label">
              {edge.count}
            </text>
          </g>
        );
      })}

      {graph.nodes.map((node) => {
        const nodeClass = NODE_CLASS_BY_TYPE[node.type] ?? NODE_CLASS_BY_TYPE.unknown;
        const nodeRadius = 18 + Math.min(node.count, 6);

        return (
          <g key={node.id} className={nodeClass} transform={`translate(${node.position.x}, ${node.position.y})`}>
            <circle r={nodeRadius} />
            <text className="graph-node__label" x={0} y={nodeRadius + 18}>
              {node.label}
            </text>
            <text className="graph-node__count" x={0} y={4}>
              {node.count}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
