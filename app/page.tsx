const links = [
  { label: "Email", href: "mailto:sudhamshu.addanki@smaddanki.com" },
  { label: "GitHub", href: "https://github.com/smaddanki" },
  { label: "LinkedIn", href: "https://linkedin.com/in/smaddanki" },
];

export default function Home() {
  return (
    <main className="wrap">
      <header>
        <p className="kicker">smaddanki.com</p>
        <h1>Sudhamshu Addanki</h1>
        <p className="lede">
          I architect data systems and conduct quantitative research at the
          intersection of data engineering, machine learning, and business
          intelligence.
        </p>
      </header>

      <section>
        <h2>Focus areas</h2>
        <ul className="areas">
          <li>Applied machine learning</li>
          <li>Time series, NLP, LLMs, recommender systems</li>
          <li>Quantitative finance</li>
        </ul>
      </section>

      <footer>
        <p className="note">Writing and projects coming soon.</p>
        <nav>
          {links.map((link) => (
            <a key={link.label} href={link.href}>
              {link.label}
            </a>
          ))}
        </nav>
      </footer>
    </main>
  );
}
