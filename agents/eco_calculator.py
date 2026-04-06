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
    def calculate_impact(self, distance_km: float, ron95: float = 2.60, ron97: float = 3.47, ron95_skps: float = 2.05) -> str:
        if distance_km <= 0:
            return "Invalid distance for calculation."
            
        # Car
        car_fuel_liters = self.CAR_LITERS_PER_KM * distance_km
        # Real cost (Subsidized)
        car_cost_real = car_fuel_liters * ron95
        # Market cost (RON97 - Simulating global volatility)
        car_cost_market = car_fuel_liters * ron97
        car_co2 = self.CAR_CO2_GRAMS_PER_KM * distance_km
        
        # Grab Ride-Hailing (Commercial SKPS Subsidy)
        # We focus on the isolated fuel cost/carbon component to compare efficiency
        grab_cost_fuel = car_fuel_liters * ron95_skps
        grab_co2 = self.CAR_CO2_GRAMS_PER_KM * distance_km
        
        # Motorbike
        moto_fuel_liters = self.MOTORBIKE_LITERS_PER_KM * distance_km
        moto_cost_real = moto_fuel_liters * ron95
        moto_cost_market = moto_fuel_liters * ron97
        moto_co2 = self.MOTORBIKE_CO2_GRAMS_PER_KM * distance_km
        
        # Public Transit (Costs are generally fixed fare)
        pt_co2 = self.PUBLIC_TRANSIT_CO2_GRAMS_PER_KM * distance_km
        
        report = (
            f"🌍 **EcoNomics Impact Report** (Distance: {distance_km:.1f} km)\n"
            f"*Source: Live Government Fuel Data (RON95: RM {ron95:.2f} | RON97: RM {ron97:.2f} | SKPS: RM {ron95_skps:.2f})*\n\n"
            f"🚗 **Personal Car (General Market)**:\n"
            f"   - Current Cost (Subsidized): RM {car_cost_real:.2f}\n"
            f"   - **Market-Volatile Cost (RON97)**: RM {car_cost_market:.2f}\n"
            f"   - Carbon Footprint: {car_co2/1000:.2f} kg CO2\n"
            f"📱 **Grab/E-Hailing (Commercial SKPS Subsidy)**:\n"
            f"   - Fuel Component Cost: RM {grab_cost_fuel:.2f} (excluding driver fare)\n"
            f"   - Carbon Footprint: {grab_co2/1000:.2f} kg CO2\n"
            f"🏍️ **Motorbike**:\n"
            f"   - Current Cost (Subsidized): RM {moto_cost_real:.2f}\n"
            f"   - **Market-Volatile Cost (RON97)**: RM {moto_cost_market:.2f}\n"
            f"   - Carbon Footprint: {moto_co2/1000:.2f} kg CO2\n"
            f"🚆 **Public Transit (LRT/MRT/Bus)**:\n"
            f"   - Estimated Fuel Cost: Shielded from Volatility\n"
            f"   - Carbon Footprint: {pt_co2/1000:.2f} kg CO2\n\n"
            f"💡 **WOW Factor**: If fuel subsidies were removed (Straits of Hormuz lockdown context), driving costs RM {car_cost_market:.2f} per trip. Public Transit saves {((car_co2 - pt_co2)/car_co2)*100:.1f}% emissions. E-Hailing operates on cheaper RM {ron95_skps:.2f} SKPS commercial fuel."
        )
        return report
