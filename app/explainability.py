import shap
import pandas as pd


def explain_prediction(model, customer_data: pd.DataFrame, top_n: int = 5):
    """
    Generate a local SHAP explanation for one customer.
    """

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["model"]

    # Transform the original customer data exactly as the model does
    transformed_data = preprocessor.transform(customer_data)

    # Get transformed feature names
    feature_names = preprocessor.get_feature_names_out()

    # Create SHAP explainer for the Random Forest
    explainer = shap.TreeExplainer(classifier)

    # Calculate SHAP values
    shap_values = explainer.shap_values(transformed_data)

    # SHAP output can differ depending on SHAP version/model
    if isinstance(shap_values, list):
        values = shap_values[1][0]
    else:
        values = shap_values[0]

    # Create feature contribution table
    explanation_df = pd.DataFrame({"feature": feature_names, "shap_value": values})

    # Sort by absolute contribution
    explanation_df["absolute_impact"] = explanation_df["shap_value"].abs()

    explanation_df = explanation_df.sort_values("absolute_impact", ascending=False)

    # Take the strongest contributors
    top_features = explanation_df.head(top_n)

    higher_risk = []
    lower_risk = []

    for _, row in top_features.iterrows():

        feature = row["feature"]
        impact = float(row["shap_value"])

        # Remove transformer prefixes
        clean_feature = feature.replace("num__", "")
        clean_feature = clean_feature.replace("cat__", "")

        item = {"feature": clean_feature, "impact": round(impact, 4)}

        if impact > 0:
            higher_risk.append(item)
        elif impact < 0:
            lower_risk.append(item)

    return {"higher_risk": higher_risk, "lower_risk": lower_risk}
