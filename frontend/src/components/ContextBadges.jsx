export default function ContextBadges({ timeWindow, meta, context }) {

  const badges = [];

  if (timeWindow) badges.push(`Window ${timeWindow}`);
  if (context?.weekday) badges.push(context.weekday);
  if (context?.weather) badges.push(context.weather);
  if (meta?.model) badges.push(`Model ${meta.model}`);
  if (meta?.dataset) badges.push("Dataset");
  if (meta?.updated) badges.push(`Updated ${meta.updated}`);

  if (badges.length === 0) return null;

  return (
    <div className="context-badges">

      <div className="context-badges-inner">

        {badges.map((badge, i) => (
          <span key={i} className="context-pill">
            {badge}
          </span>
        ))}

      </div>

    </div>
  );
}