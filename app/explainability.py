import shap
import pandas as pd


def explain_prediction(model, customer_data: pd.DataFrame, top_n: int = 5):
    """
    Generate a local SHAP explanation for one customer.
    """

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["model"]

    # Apply the same preprocessing used by the trained model
    transformed_data = preprocessor.transform(customer_data)

    # Get transformed feature names
    feature_names = preprocessor.get_feature_names_out()

    # SHAP explainer for Random Forest
    explainer = shap.TreeExplainer(classifier)

    # Calculate SHAP values
    shap_values = explainer.shap_values(transformed_data)

    # SHAP 0.52 can return:
    # (samples, features, classes)
    # For churn ("Yes"), class index 1 is used.
    if isinstance(shap_values, list):
        values = shap_values[1][0]
    elif len(shap_values.shape) == 3:
        values = shap_values[0, :, 1]
    else:
        values = shap_values[0]

    values = values.flatten()

    # Safety check
    if len(feature_names) != len(values):
        raise ValueError(
            f"Feature/SHAP mismatch: "
            f"{len(feature_names)} features vs {len(values)} SHAP values"
        )

    # Keep only features that are actually active for this customer.
    # Numeric features are always retained.
    active_features = []

    for i, feature in enumerate(feature_names):
        if feature.startswith("num__"):
            active_features.append(True)
        else:
            active_features.append(transformed_data[0, i] != 0)

    explanation_df = pd.DataFrame(
        {"feature": feature_names, "shap_value": values, "active": active_features}
    )

    explanation_df = explanation_df[explanation_df["active"]].copy()

    explanation_df["absolute_impact"] = explanation_df["shap_value"].abs()

    explanation_df = explanation_df.sort_values("absolute_impact", ascending=False)

    top_features = explanation_df.head(top_n)

    higher_risk = []
    lower_risk = []

    for _, row in top_features.iterrows():

        feature = row["feature"]
        impact = float(row["shap_value"])

        clean_feature = feature.replace("num__", "")
        clean_feature = clean_feature.replace("cat__", "")

        item = {"feature": clean_feature, "impact": round(impact, 4)}

        if impact > 0:
            higher_risk.append(item)

        elif impact < 0:
            lower_risk.append(item)

    return {"higher_risk": higher_risk, "lower_risk": lower_risk}
