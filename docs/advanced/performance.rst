Performance Optimization Guide
==============================

Best practices for optimizing Flask-Exts applications for performance and scalability.

Database Optimization
---------------------

Query Optimization
~~~~~~~~~~~~~~~~~~~

Eager Loading with Relationships
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Avoid N+1 query problem using eager loading::

    from sqlalchemy.orm import joinedload

    # Bad: N+1 queries
    posts = Post.query.all()
    for post in posts:
        print(post.author.name)  # Separate query for each post

    # Good: Single query with join
    posts = Post.query.options(joinedload(Post.author)).all()
    for post in posts:
        print(post.author.name)  # No additional queries

Selective Column Loading
^^^^^^^^^^^^^^^^^^^^^^^^

Load only needed columns::

    from sqlalchemy import select

    # Load only necessary columns
    posts = Post.query.with_entities(
        Post.id, Post.title, Post.created_at
    ).all()

Batch Operations
^^^^^^^^^^^^^^^^

Use batch operations for bulk updates::

    from sqlalchemy import update

    # Inefficient: Multiple individual updates
    for post in posts:
        post.published = True
        db.session.add(post)
    db.session.commit()

    # Efficient: Single batch update
    db.session.execute(
        update(Post).values(published=True)
    )
    db.session.commit()

Caching Strategies
~~~~~~~~~~~~~~~~~~

Query Result Caching
^^^^^^^^^^^^^^^^^^^^

Cache frequently accessed data::

    from flask_caching import Cache

    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

    @cache.cached(timeout=3600)
    def get_popular_posts():
        return Post.query.filter(
            Post.views > 1000
        ).all()

Selective Caching
^^^^^^^^^^^^^^^^^

Cache strategically::

    # Cache expensive aggregations
    @cache.cached(timeout=300, key_prefix='stats_')
    def get_post_statistics():
        return {
            'total': Post.query.count(),
            'today': Post.query.filter(
                Post.created_at >= datetime.utcnow().date()
            ).count()
        }

Cache Invalidation
^^^^^^^^^^^^^^^^^^

Keep cache fresh::

    from myapp import cache

    def create_post(title, content):
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()

        # Invalidate caches
        cache.delete_memoized(get_popular_posts)
        cache.delete('stats_')

        return post

Indexing
~~~~~~~~

Add Strategic Indexes
^^^^^^^^^^^^^^^^^^^^^

::

    from sqlalchemy import Index

    class Post(db.Model):
        id: Mapped[int] = mapped_column(primary_key=True)
        title: Mapped[str] = mapped_column(String(200))
        slug: Mapped[str] = mapped_column(String(200), unique=True)
        status: Mapped[str] = mapped_column(String(20), index=True)
        created_at: Mapped[datetime] = mapped_column(index=True)

        # Composite index for common filter combinations
        __table_args__ = (
            Index('idx_status_created', 'status', 'created_at'),
        )

Frontend Optimization
---------------------

Static File Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

Compress CSS and JavaScript
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use minification tools::

    # Use Flask-Assets for automatic minification
    from flask_assets import Environment, Bundle

    assets = Environment(app)
    js_all = Bundle(
        'js/jquery.js',
        'js/bootstrap.js',
        'js/app.js',
        filters='jsmin',
        output='gen/packed.js'
    )
    css_all = Bundle(
        'css/bootstrap.css',
        'css/app.css',
        filters='cssmin',
        output='gen/packed.css'
    )
    assets.register('js_all', js_all)
    assets.register('css_all', css_all)

Use CDN for External Libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    <!-- Instead of serving locally -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/js/bootstrap.bundle.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/css/bootstrap.min.css">

Enable Gzip Compression
^^^^^^^^^^^^^^^^^^^^^^^

::

    # In nginx configuration
    gzip on;
    gzip_types text/plain text/css text/javascript application/json;
    gzip_min_length 1000;
    gzip_level 6;

Browser Caching
^^^^^^^^^^^^^^^

Set appropriate cache headers::

    @app.after_request
    def set_cache_headers(response):
        # Cache static files for 1 year
        if response.mimetype.startswith('image') or \
           response.mimetype in ['text/css', 'application/javascript']:
            response.cache_control.max_age = 31536000
        else:
            # Don't cache HTML pages
            response.cache_control.no_cache = True
        return response

Template Optimization
~~~~~~~~~~~~~~~~~~~~~

Reduce Template Complexity
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Keep templates simple and fast::

    {# Avoid: Complex logic in templates #}
    {% if current_user.is_authenticated and \
          current_user.role.permissions.filter(
              Permission.name == 'admin'
          ).count() > 0 %}
        Admin panel
    {% endif %}

    {# Better: Prepare data in view #}
    {% if user_is_admin %}
        Admin panel
    {% endif %}

Use Template Caching
^^^^^^^^^^^^^^^^^^^^

::

    # Enable template caching in production
    app.config['TEMPLATES_AUTO_RELOAD'] = False

Use Macros for Reusable Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    {% macro render_post(post) %}
        <article>
            <h2>{{ post.title }}</h2>
            <p>{{ post.content[:200] }}...</p>
        </article>
    {% endmacro %}

Application Optimization
-------------------------

Lazy Loading
~~~~~~~~~~~~

Load modules and components only when needed::

    # Instead of importing everything at startup
    from importlib import import_module

    def get_blueprint(name):
        module = import_module(f'myapp.blueprints.{name}')
        return module.bp

View Function Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reduce response time::

    # Inefficient: Load all data
    @app.route('/posts')
    def list_posts():
        posts = Post.query.all()  # Loads everything into memory
        return render_template('posts.html', posts=posts)

    # Better: Paginate
    from flask_sqlalchemy import Pagination

    @app.route('/posts')
    def list_posts():
        page = request.args.get('page', 1, type=int)
        paginated = Post.query.paginate(page=page, per_page=20)
        return render_template('posts.html', posts=paginated.items)

Async Views
~~~~~~~~~~~

Handle long-running operations asynchronously::

    from flask import request
    from celery import Celery

    celery = Celery(app.name)

    @app.route('/export', methods=['POST'])
    def export_data():
        # Start async task
        task = export_data_task.delay()
        return jsonify({'task_id': task.id}), 202

    @celery.task
    def export_data_task():
        # Long-running operation
        data = Post.query.all()
        # Generate and save file
        return {'status': 'complete'}

Connection Pooling
~~~~~~~~~~~~~~~~~~

Optimize database connections::

    from sqlalchemy.pool import QueuePool

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'poolclass': QueuePool,
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

Request/Response Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Minimize Response Size
^^^^^^^^^^^^^^^^^^^^^^

Use JSON instead of HTML for APIs::

    # Inefficient: Return HTML with heavy templating
    @app.route('/api/posts')
    def get_posts_html():
        posts = Post.query.all()
        return render_template('posts.html', posts=posts)

    # Better: Return JSON
    @app.route('/api/posts')
    def get_posts():
        posts = Post.query.limit(20).all()
        return jsonify([{
            'id': p.id,
            'title': p.title,
        } for p in posts])

Streaming Large Responses
^^^^^^^^^^^^^^^^^^^^^^^^^

::

    from flask import stream_with_context

    @app.route('/export/large')
    def export_large():
        def generate():
            for post in Post.query.yield_per(100):
                yield f'{post.id},{post.title}\n'

        return app.response_class(
            generate(),
            mimetype='text/csv'
        )

Monitoring and Profiling
------------------------

Application Profiling
~~~~~~~~~~~~~~~~~~~~~

Identify performance bottlenecks::

    from flask_debugtoolbar import DebugToolbarExtension

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension(app)

    # Analyze:
    # - Query count and time
    # - Template rendering time
    # - Total request time

Query Analysis
~~~~~~~~~~~~~~

Log slow queries::

    app.config['SQLALCHEMY_ECHO'] = True  # Log all queries
    app.config['SQLALCHEMY_RECORD_QUERIES'] = True

    from flask_sqlalchemy import get_debug_queries

    @app.after_request
    def after_request(response):
        for query in get_debug_queries():
            if query.duration >= 0.5:
                app.logger.warning(
                    f'Slow query: {query.statement}\n'
                    f'Time: {query.duration}s'
                )
        return response

Metrics Collection
~~~~~~~~~~~~~~~~~~~

Track application performance::

    from prometheus_client import Counter, Histogram

    request_count = Counter(
        'app_requests_total',
        'Total requests',
        ['method', 'endpoint']
    )
    request_duration = Histogram(
        'app_request_duration_seconds',
        'Request duration in seconds'
    )

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        duration = time.time() - g.start_time
        request_count.labels(
            method=request.method,
            endpoint=request.endpoint
        ).inc()
        request_duration.observe(duration)
        return response

Deployment Optimization
------------------------

Web Server Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use production WSGI server::

    # Use Gunicorn with multiple workers
    # gunicorn -w 4 -b 0.0.0.0:8000 myapp:app

    # Configuration
    app.config['PROPAGATE_EXCEPTIONS'] = True

Load Balancing
~~~~~~~~~~~~~~

Distribute traffic::

    # nginx configuration
    upstream flask_app {
        server 127.0.0.1:8000;
        server 127.0.0.1:8001;
        server 127.0.0.1:8002;
    }

    server {
        listen 80;
        location / {
            proxy_pass http://flask_app;
        }
    }

Performance Checklist
---------------------

Database
  ☐ Use indexes for frequently queried columns
  ☐ Use eager loading to prevent N+1 queries
  ☐ Cache expensive queries
  ☐ Use connection pooling
  ☐ Optimize batch operations

Frontend
  ☐ Minify CSS and JavaScript
  ☐ Use CDN for external libraries
  ☐ Enable gzip compression
  ☐ Set appropriate cache headers
  ☐ Compress images

Application
  ☐ Use pagination for large datasets
  ☐ Implement caching strategy
  ☐ Use async for long-running tasks
  ☐ Keep templates simple
  ☐ Optimize database queries

Monitoring
  ☐ Profile application regularly
  ☐ Log slow queries
  ☐ Monitor response times
  ☐ Track resource usage
  ☐ Set up alerts

See Also
--------

- `SQLAlchemy Performance <https://docs.sqlalchemy.org/performance.html>`_
- `Flask Best Practices <https://flask.palletsprojects.com/>`_
- `nginx Configuration <https://nginx.org/en/docs/>`_
- :doc:`modelview` - Admin optimization
