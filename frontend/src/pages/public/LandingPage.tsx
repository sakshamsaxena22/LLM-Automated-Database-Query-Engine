import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Brain, Database, Shield, Zap, BarChart3, ArrowRight } from 'lucide-react';

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Queries',
    desc: 'Translate natural language into optimized database queries with our RAG-based intelligence engine.',
  },
  {
    icon: Database,
    title: 'Multi-Database Support',
    desc: 'MongoDB today, PostgreSQL, MySQL, and more tomorrow. One interface for all your data.',
  },
  {
    icon: Shield,
    title: 'Enterprise Security',
    desc: 'Role-based access, query validation, risk scoring, and comprehensive audit trails.',
  },
  {
    icon: Zap,
    title: 'Real-Time Performance',
    desc: 'Redis caching, query optimization, and sub-second response times for enterprise workloads.',
  },
  {
    icon: BarChart3,
    title: 'Analytics Dashboard',
    desc: 'Monitor query patterns, usage metrics, and system health from a beautiful dashboard.',
  },
];

export function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      {/* Ambient glow */}
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute left-1/4 top-0 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-primary/5 blur-[120px]" />
        <div className="absolute right-1/4 top-1/3 h-[500px] w-[500px] rounded-full bg-chart-5/5 blur-[120px]" />
      </div>

      {/* Navbar */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-6 mx-auto max-w-7xl">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl animated-gradient">
            <Brain className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold gradient-text">AI Data Platform</span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            to="/login"
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            Sign In
          </Link>
          <Link
            to="/register"
            className="rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-all hover:bg-primary/90 glow-primary"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 mx-auto max-w-7xl px-8 pt-20 pb-32 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-4 py-1.5 text-xs font-medium text-muted-foreground backdrop-blur-sm">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse" />
            Enterprise-Grade AI Database Operations
          </div>

          <h1 className="mx-auto max-w-4xl text-5xl font-extrabold leading-tight tracking-tight text-foreground md:text-7xl">
            Talk to Your <span className="gradient-text">Database</span> in Plain English
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            Transform how your team interacts with data. Our AI understands your intent,
            validates queries for safety, and delivers results in milliseconds — no SQL required.
          </p>

          <div className="mt-10 flex items-center justify-center gap-4">
            <Link
              to="/register"
              className="group flex items-center gap-2 rounded-xl bg-primary px-8 py-3.5 text-sm font-semibold text-primary-foreground transition-all hover:bg-primary/90 glow-primary"
            >
              Start Free Trial
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              to="/login"
              className="rounded-xl border border-border px-8 py-3.5 text-sm font-semibold text-foreground transition-all hover:bg-accent"
            >
              Live Demo
            </Link>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          className="mx-auto mt-20 grid max-w-3xl grid-cols-3 gap-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          {[
            ['10x', 'Faster Queries'],
            ['99.9%', 'Uptime SLA'],
            ['50+', 'Integrations'],
          ].map(([stat, label]) => (
            <div key={label} className="text-center">
              <div className="text-3xl font-bold gradient-text">{stat}</div>
              <div className="mt-1 text-sm text-muted-foreground">{label}</div>
            </div>
          ))}
        </motion.div>
      </section>

      {/* Features */}
      <section className="relative z-10 mx-auto max-w-7xl px-8 pb-32">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-foreground">Enterprise-Ready Features</h2>
          <p className="mt-3 text-muted-foreground">
            Built for scale. Designed for security. Powered by AI.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map(({ icon: Icon, title, desc }, i) => (
            <motion.div
              key={title}
              className="glass rounded-2xl p-6 transition-all duration-300 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 * i }}
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                <Icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-foreground">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="relative z-10 mx-auto max-w-7xl px-8 pb-20">
        <div className="relative overflow-hidden rounded-3xl animated-gradient p-[1px]">
          <div className="rounded-3xl bg-background p-12 text-center">
            <h2 className="text-3xl font-bold text-foreground">Ready to Transform Your Data Workflow?</h2>
            <p className="mx-auto mt-4 max-w-xl text-muted-foreground">
              Join thousands of teams using AI to unlock insights from their databases.
            </p>
            <Link
              to="/register"
              className="mt-8 inline-flex items-center gap-2 rounded-xl bg-primary px-10 py-4 text-sm font-semibold text-primary-foreground transition-all hover:bg-primary/90 glow-primary"
            >
              Get Started Free <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border py-8 text-center text-xs text-muted-foreground">
        © 2024 Enterprise AI Data Platform. All rights reserved.
      </footer>
    </div>
  );
}
