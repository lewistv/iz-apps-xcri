import { Link } from 'react-router-dom';
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
            <Link key={idx} to={link.href} className="explainer-link">
              {link.text} →
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
