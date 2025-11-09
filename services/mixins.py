# CHANGED: Created mixins for services app

from django.db.models import QuerySet, Prefetch
from labels.models import Label


class PriceFilterByWeddingDateMixin:
    """
    Filters prices to show only those applicable to the customer's wedding date using the rule engine.
    CHANGED: Now supports both customer and agent pricing rules based on user type
    """
    
    def _get_pricing_trigger_code(self, wedding_year, is_agent=False):
        """
        CHANGED: Get the trigger code for a given wedding year
        CHANGED: Support both customer and agent pricing triggers
        
        Customer triggers:
        - 2026: pricing_trigger_2026_2027
        - 2027: pricing_trigger_2027_2028
        
        Agent triggers:
        - 2026: pricing_trigger_2026_2027_Agent
        - 2027: pricing_trigger_2027_2028_Agent
        """
        # CHANGED: Use agent suffix if is_agent is True
        agent_suffix = '_Agent' if is_agent else ''
        
        trigger_mapping = {
            2026: f'pricing_trigger_2026_2027{agent_suffix}',
            2027: f'pricing_trigger_2027_2028{agent_suffix}',
            2028: f'pricing_trigger_2028_2029{agent_suffix}',
            2029: f'pricing_trigger_2029_2030{agent_suffix}',
            2030: f'pricing_trigger_2030_2031{agent_suffix}',
        }
        return trigger_mapping.get(wedding_year)
    
    def _is_user_agent(self, user):
        """
        CHANGED: Determine if the current user is an agent
        """
        if not user or not user.is_authenticated:
            return False
        
        try:
            from users.models import Agent
            # CHANGED: Check if user has agent profile
            agent = user.agent_profile
            return agent and agent.status == Agent.StatusChoices.ACTIVE
        except:
            return False
    
    def get_filtered_prices_for_customer(self, prices_queryset, customer, user=None, wedding_date=None):
        """
        Filter prices based on customer's wedding date and pricing rules.
        CHANGED: Now supports agent-created orders with no customer (uses wedding_date parameter)
        
        Args:
            prices_queryset: QuerySet of Price objects
            customer: Customer object with wedding_day (optional for agent-created orders)
            user: The current user (optional, used to determine if agent)
            wedding_date: Wedding date to use (optional, for agent-created orders without customer)
            
        Returns:
            Filtered QuerySet of applicable prices
        """
        # CHANGED: Handle agent-created orders with no customer by using wedding_date parameter
        actual_wedding_date = None
        
        if customer and hasattr(customer, 'wedding_day') and customer.wedding_day:
            actual_wedding_date = customer.wedding_day
        elif wedding_date:
            actual_wedding_date = wedding_date
        
        if not actual_wedding_date:
            # CHANGED: Return all active prices if no wedding date set
            return prices_queryset.filter(is_active=True)
        
        # CHANGED: Determine if current user is an agent
        is_agent = self._is_user_agent(user) if user else False
        
        # CHANGED: Get the trigger code for this wedding year (agent or customer)
        wedding_year = actual_wedding_date.year
        trigger_code = self._get_pricing_trigger_code(wedding_year, is_agent=is_agent)
        
        if not trigger_code:
            # CHANGED: No trigger found for this year, return all active prices
            return prices_queryset.filter(is_active=True)
        
        # CHANGED: Filter prices by checking if rule engine allows them
        from rules.engine import process_rules
        
        applicable_prices = []
        
        for price in prices_queryset.filter(is_active=True):
            # CHANGED: Use rule engine with dynamic trigger code based on wedding year and user type
            # The rule engine will check the price's labels against the trigger
            rule_result = process_rules(target_entity=price, event_code=trigger_code)
            
            # CHANGED: If rule processing indicates this price is applicable, include it
            if rule_result:
                applicable_prices.append(price.pk)
        
        # CHANGED: Return queryset filtered by applicable price IDs
        return prices_queryset.filter(pk__in=applicable_prices)

    def get_filtered_service_prices(self, service, customer, user=None, wedding_date=None):
        """
        CHANGED: Filter service-level prices based on customer's wedding date and pricing rules.
        
        Args:
            service: Service object
            customer: Customer object with wedding_day (optional for agent-created orders)
            user: The current user (optional, used to determine if agent)
            wedding_date: Wedding date to use (optional, for agent-created orders without customer)
            
        Returns:
            Filtered QuerySet of applicable service-level prices
        """
        service_prices = service.get_service_prices()
        return self.get_filtered_prices_for_customer(
            service_prices,
            customer,
            user=user,
            wedding_date=wedding_date
        )
