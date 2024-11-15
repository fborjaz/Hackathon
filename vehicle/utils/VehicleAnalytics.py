import numpy as np
from sklearn.linear_model import LinearRegression
from carbon_footprint import settings
from vehicle.models import Vehicle
from openai import OpenAI
import pandas as pd


class VehicleDataAnalytics:
    def __init__(self):
        self.model_engine = "gpt-4o-mini" 
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    def _generate_response(self, context, question):
        try:
            response = self.client.chat.completions.create(
                model=self.model_engine,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": question}
                ],
                temperature=0.5,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error al interactuar con ChatGPT: {str(e)}"

    def predict_co2_emissions(self, engine_size, cylinders, fuel_consumption_comb):
        """
        Predice las emisiones de CO₂ basado en características del vehículo.
        """
        vehicles = Vehicle.objects.all().values(
            'engine_size', 'cylinders', 'fuel_consumption_comb', 'co2_emissions'
        )
        if not vehicles:
            return {
                "message": "No hay suficientes datos para realizar la predicción.",
                "details": None,
                "recommendations": "Por favor, agrega más datos sobre vehículos para mejorar los análisis."
            }

        # Preparar datos
        X = np.array([
            [v['engine_size'], v['cylinders'], v['fuel_consumption_comb']]
            for v in vehicles
        ])
        y = np.array([v['co2_emissions'] for v in vehicles])

        # Modelo de predicción
        model = LinearRegression()
        model.fit(X, y)
        prediction = model.predict([[engine_size, cylinders, fuel_consumption_comb]])

        # Contexto para ChatGPT
        context = (
            "Eres un asistente especializado en análisis de datos de vehículos y cambio climático. "
            "Tu tarea es proporcionar explicaciones claras sobre predicciones de emisiones de CO₂ y cómo optimizarlas."
            "devuel tu respuesta en markdown."
        )
        question = (
            f"El motor tiene un tamaño de {engine_size} litros, {cylinders} cilindros, y un consumo de combustible combinado de {fuel_consumption_comb} L/100km. "
            f"El modelo predice emisiones de CO₂ de aproximadamente {round(prediction[0], 2)} g/km. "
            "¿Qué recomendaciones puedes ofrecer para reducir estas emisiones?"
        )

        # Generar respuesta enriquecida
        enriched_response = self._generate_response(context, question)

        return {
            "message": "Predicción completada.",
            "prediction": round(prediction[0], 2),
            "details": {
                "average_co2": round(np.mean(y), 2),
                "max_co2": np.max(y),
                "min_co2": np.min(y)
            },
            "chatgpt_recommendations": enriched_response
        }

    def classify_efficiency(self, engine_size, fuel_consumption_comb):
        """
        Clasifica un vehículo como eficiente o ineficiente y genera explicaciones.
        """
        efficiency_threshold = 130  # g/km como referencia
        vehicles = Vehicle.objects.all().values(
            'engine_size', 'fuel_consumption_comb', 'co2_emissions'
        )
        if not vehicles:
            return {
                "message": "No hay datos suficientes para la clasificación.",
                "details": None,
                "recommendations": "Por favor, agrega datos sobre eficiencia vehicular."
            }

        # Clasificación basada en reglas simples
        classification = (
            "Eficiente" if fuel_consumption_comb <= efficiency_threshold else "Ineficiente"
        )

        # Contexto para ChatGPT
        context = (
            "Eres un experto en eficiencia vehicular y sostenibilidad. "
            "Proporciona explicaciones claras y sugerencias prácticas para vehículos eficientes."
            "Proporciona una respuesta corta y concisa para el propietario del vehículo."
        )
        question = (
            f"Un vehículo con un tamaño de motor de {engine_size} litros y un consumo de {fuel_consumption_comb} L/100km "
            f"se clasifica como {classification}. ¿Cómo puede el propietario mejorar su eficiencia?"
        )

        # Generar respuesta enriquecida
        enriched_response = self._generate_response(context, question)

        return {
            "message": "Clasificación completada.",
            "classification": classification,
            "chatgpt_recommendations": enriched_response
        }

    def analyze_make_co2_trends(self, make):
        """
        Analiza cómo un fabricante ('make') ha mejorado o empeorado sus emisiones de CO₂
        con respecto al año de fabricación.
        """
        vehicles = Vehicle.objects.filter(make=make).values(
            'year_of_manufacture', 'co2_emissions'
        )
        if not vehicles:
            return {
                "message": f"No se encontraron datos para el fabricante '{make}'.",
                "details": None
            }

        # Convertir datos a un DataFrame para análisis
        data = pd.DataFrame(vehicles)

        # Agrupar por año y calcular el promedio de emisiones
        trends = data.groupby('year_of_manufacture')['co2_emissions'].mean().reset_index()
        trends['co2_emissions_change'] = trends['co2_emissions'].diff()

        # Reemplazar NaN en la columna 'co2_emissions_change' con 0
        trends['co2_emissions_change'].fillna(0, inplace=True)

        # Evaluar si el fabricante ha mejorado o empeorado
        last_year = trends.iloc[-1]
        first_year = trends.iloc[0]
        overall_change = last_year['co2_emissions'] - first_year['co2_emissions']
        trend_description = (
            "mejorado" if overall_change < 0 else "empeorado"
        )

        # Contexto para ChatGPT
        context = (
            f"Eres un analista experto en sostenibilidad vehicular. Proporciona un análisis "
            f"detallado sobre cómo el fabricante '{make}' ha {'mejorado' if overall_change < 0 else 'empeorado'} "
            f"las emisiones de CO₂ de sus vehículos con base en los datos históricos."
        )
        question = (
            f"El fabricante '{make}' tiene un cambio total en las emisiones de CO₂ de "
            f"{round(overall_change, 2)} g/km entre {int(first_year['year_of_manufacture'])} y {int(last_year['year_of_manufacture'])}. "
            f"Proporcione ideas para continuar mejorando las emisiones."
        )

        enriched_response = self._generate_response(context, question)

        return {
            "message": "Análisis completado.",
            "make": make,
            "trends": trends.to_dict(orient='records'),
            "overall_change": round(overall_change, 2),
            "trend_description": trend_description,
            "chatgpt_recommendations": enriched_response
        }
