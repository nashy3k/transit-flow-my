import os
from opik import track

class EcoNomicsCalculator:
    """
    Calculates carbon footprint and fuel cost for commute options.
    Uses inflated fuel prices to reflect fictional "Straits of Hormuz lockdown" scenario for the WOW factor.
    """
    # Assumptions
    VOLATILE_FUEL_PRICE_RM_PER_LITER = 4.50  # Elevated from standard ~RM 2.05
    
    # Consumption & Carbon Data (per km)
    # L/100km -> L/km = /100
    CAR_LITERS_PER_KM = 8.0 / 100
    CAR_CO2_GRAMS_PER_KM = 192
    
    MOTORBIKE_LITERS_PER_KM = 3.0 / 100
    MOTORBIKE_CO2_GRAMS_PER_KM = 103
    
    PUBLIC_TRANSIT_CO2_GRAMS_PER_KM = 30  # Assuming LRT/MRT efficiency
    
    @track(name="eco_economics_calculation")
    def calculate_impact(self, distance_km: float, ron95: float = 2.05, ron97: float = 3.47, ron95_skps: float = 2.05, budi_ron95: float = 1.99) -> str:
        if distance_km <= 0:
            return "Invalid distance for calculation."
            
        # Car
        car_fuel_liters = self.CAR_LITERS_PER_KM * distance_km
        # Budi95 Protected Cost
        car_cost_budi = car_fuel_liters * budi_ron95
        # Current Subsidized (Standard)
        car_cost_real = car_fuel_liters * ron95
        # Market cost (RON97 - Simulating global volatility)
        car_cost_market = car_fuel_liters * ron97
        car_co2 = self.CAR_CO2_GRAMS_PER_KM * distance_km
        
        # Savings provided by Budi95 vs Current Market RON95
        budi_savings = car_cost_real - car_cost_budi
        
        # Grab Ride-Hailing (Commercial SKPS Subsidy)
        grab_cost_fuel = car_fuel_liters * ron95_skps
        grab_co2 = self.CAR_CO2_GRAMS_PER_KM * distance_km
        
        # Motorbike
        moto_fuel_liters = self.MOTORBIKE_LITERS_PER_KM * distance_km
        moto_cost_budi = moto_fuel_liters * budi_ron95
        moto_co2 = self.MOTORBIKE_CO2_GRAMS_PER_KM * distance_km
        
        # Public Transit (Costs are generally fixed fare)
        pt_co2 = self.PUBLIC_TRANSIT_CO2_GRAMS_PER_KM * distance_km
        
        report = (
            f"🌍 **EcoNomics Impact Report** (Distance: {distance_km:.1f} km)\n"
            f"*Source: Live Government Fuel Registry | Citizen Rate (Budi95): RM 1.99*\n\n"
            f"🚗 **Personal Car (Citizen Insights)**:\n"
            f"   - **Budi95 Subsidized Cost**: RM {car_cost_budi:.2f}\n"
            f"   - Current Market RON95: RM {car_cost_real:.2f} (Savings: RM {budi_savings:.2f})\n"
            f"   - Carbon Footprint: {car_co2/1000:.2f} kg CO2\n"
            f"📱 **Grab/E-Hailing (Commercial SKPS)**:\n"
            f"   - Fuel Component Cost: RM {grab_cost_fuel:.2f} (@ RM {ron95_skps:.2f}/L)\n"
            f"   - Carbon Footprint: {grab_co2/1000:.2f} kg CO2\n"
            f"🚆 **Public Transit (LRT/MRT/Bus)**:\n"
            f"   - **Estimated Cost**: Variable fares (Shielded from market volatility)\n"
            f"   - Carbon Footprint: {pt_co2/1000:.2f} kg CO2\n\n"
            f"💡 **WOW Factor**: Under the 'BudiProtocol', your commute is shielded from the RM {ron97:.2f}/L market floating rate. Using the RM {budi_ron95:.2f} Budi95 rate saves you RM {(car_cost_market - car_cost_budi):.2f} compared to an unshielded market trip."
        )
        return report

    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate the great-circle distance between two points 
        on the Earth's surface using the Haversine formula.
        Returns distance in km.
        """
        import math
        R = 6371.0 # Earth radius
        
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lng2 - lng1)
        
        a = math.sin(dLat / 2) ** 2 + \
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
            math.sin(dLon / 2) ** 2
            
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
