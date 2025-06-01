from django import template
from django.core.cache import cache
from django.utils.safestring import mark_safe
import hashlib

register = template.Library()

@register.tag('cache_fragment')
def do_cache(parser, token):
    """
    Template tag that caches the contents of a template fragment for a given amount
    of time.

    Usage:
    {% load cache_tags %}
    {% cache_fragment [key] [timeout_in_seconds] %}
        ... expensive template content ...
    {% endcache_fragment %}
    """
    nodelist = parser.parse(('endcache_fragment',))
    parser.delete_first_token()
    
    tokens = token.split_contents()
    if len(tokens) < 3:
        raise template.TemplateSyntaxError(
            "%r tag requires at least 2 arguments." % tokens[0]
        )
    
    key = tokens[1]
    timeout = tokens[2]
    
    return CacheNode(nodelist, key, timeout)

class CacheNode(template.Node):
    def __init__(self, nodelist, key, timeout):
        self.nodelist = nodelist
        self.key = template.Variable(key)
        self.timeout = template.Variable(timeout)
    
    def render(self, context):
        try:
            key = self.key.resolve(context)
            timeout = int(self.timeout.resolve(context))
        except template.VariableDoesNotExist:
            return self.nodelist.render(context)
        
        # Create a unique cache key
        cache_key = f"template_cache:{key}"
        
        # Try to get the cached content
        content = cache.get(cache_key)
        
        if content is None:
            # If not in cache, render the template and store it
            content = self.nodelist.render(context)
            cache.set(cache_key, content, timeout)
        
        return mark_safe(content)

@register.filter
def hash_id(value):
    """
    Creates a hash of the given value, useful for creating unique IDs.
    
    Usage:
    {{ object.id|hash_id }}
    """
    return hashlib.md5(str(value).encode()).hexdigest()[:8]

