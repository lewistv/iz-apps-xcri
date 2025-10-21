import './ExplainerBox.css';

export default function ExplainerBox({ title, children, links = [] }) {
  return (
    <div className="explainer-box">
      <h3 className="explainer-title">{title}</h3>
      <div className="explainer-content">
        {children}
      </div>
      {links.length > 0 && (
        <div className="explainer-links">
          {links.map((link, idx) => (
            <a key={idx} href={link.href} className="explainer-link">
              {link.text} →
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
