import os

class EcoNomicsCalculator:
    """
    Calculates carbon footprint and fuel cost for commute options.
    Uses inflated fuel prices to reflect fictional "Straits of Hormuz lockdown" scenario for the WOW factor.
    """
    # Assumptions
    VOLATILE_FUEL_PRICE_RM_PER_LITER = 3.87  # Matches README Market Rate
    
    # Consumption & Carbon Data (per km)
    # L/100km -> L/km = /100
    CAR_LITERS_PER_KM = 8.0 / 100
    CAR_CO2_GRAMS_PER_KM = 192
    
    MOTORBIKE_LITERS_PER_KM = 3.0 / 100
    MOTORBIKE_CO2_GRAMS_PER_KM = 103
    
    PUBLIC_TRANSIT_CO2_GRAMS_PER_KM = 30  # Assuming LRT/MRT efficiency
    
    def calculate_impact(self, distance_km: float, ron95: float = 3.87, ron97: float = 4.50, ron95_skps: float = 2.05, budi_ron95: float = 2.05) -> str:
        if distance_km <= 0:
            return "Invalid distance for calculation."
            
        # Car
        car_fuel_liters = self.CAR_LITERS_PER_KM * distance_km
        # Budi95 Protected Cost
        car_cost_budi = car_fuel_liters * budi_ron95
        # Market cost (Unsubsidized RM 3.87)
        car_cost_market = car_fuel_liters * ron95
        car_co2 = self.CAR_CO2_GRAMS_PER_KM * distance_km
        
        # Savings provided by Budi95 vs Unsubsidized Market
        car_savings = car_cost_market - car_cost_budi
        
        # Motorbike
        moto_fuel_liters = self.MOTORBIKE_LITERS_PER_KM * distance_km
        moto_cost_budi = moto_fuel_liters * budi_ron95
        moto_cost_market = moto_fuel_liters * ron95
        moto_co2 = self.MOTORBIKE_CO2_GRAMS_PER_KM * distance_km
        moto_savings = moto_cost_market - moto_cost_budi

        # Grab E-Hailing
        grab_fare = 5.00 + (1.50 * distance_km)
        grab_fuel_liters = self.CAR_LITERS_PER_KM * distance_km
        grab_fuel_cost_skps = grab_fuel_liters * budi_ron95 # RM 2.05 SKPS
        grab_fuel_cost_market = grab_fuel_liters * ron95    # RM 3.87 Market
        grab_driver_savings = grab_fuel_cost_market - grab_fuel_cost_skps
        grab_co2 = self.CAR_CO2_GRAMS_PER_KM * distance_km

        # Public Transit (Costs are generally fixed fare)
        pt_co2 = self.PUBLIC_TRANSIT_CO2_GRAMS_PER_KM * distance_km
        
        report = (
            f"🌍 **EcoNomics Impact Report** (Distance: {distance_km:.1f} km)\n"
            f"*Source: April 2026 Firestore Cache | Market Rate: RM 3.87 | Budi95/SKPS: RM 2.05*\n\n"
            f"🚗 **Personal Car (Citizen Insights)**:\n"
            f"   - **Budi95 Subsidized Cost**: RM {car_cost_budi:.2f}\n"
            f"   - Unsubsidized Market Cost: RM {car_cost_market:.2f} (Savings: RM {car_savings:.2f})\n"
            f"   - Carbon Footprint: {car_co2/1000:.2f} kg CO2\n"
            f"🏍️ **Motorbike (Budi95 Rated)**:\n"
            f"   - **Estimated Fuel Cost**: RM {moto_cost_budi:.2f}\n"
            f"   - Unsubsidized Market Cost: RM {moto_cost_market:.2f} (Savings: RM {moto_savings:.2f})\n"
            f"   - Carbon Footprint: {moto_co2/1000:.2f} kg CO2\n"
            f"🚕 **Grab (E-Hailing Service)**:\n"
            f"   - **Estimated Trip Fare**: RM {grab_fare:.2f}\n"
            f"   - SKPS Driver Benefit: RM {grab_fuel_cost_skps:.2f} fuel (@ RM 1.99)\n"
            f"   - *Note: Driver saves RM {grab_driver_savings:.2f} per trip via SKPS 2.0 system*\n"
            f"   - Carbon Footprint: {grab_co2/1000:.2f} kg CO2\n"
            f"🚆 **Public Transit (LRT/MRT/Bus)**:\n"
            f"   - **Estimated Cost**: Variable fares (Shielded from market volatility)\n"
            f"   - Carbon Footprint: {pt_co2/1000:.2f} kg CO2\n\n"
            f"💡 **WOW Factor**: Under the 'BudiProtocol', your commute is shielded from the RM {ron95:.2f}/L market rate. Total journey savings: RM {(car_savings):.2f} (Car) / RM {(moto_savings):.2f} (Bike) / RM {(grab_driver_savings):.2f} (Grab Driver)."
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
