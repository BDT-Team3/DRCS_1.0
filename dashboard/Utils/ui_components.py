
"""
    UI components for the dashboard.
"""

# Utilities
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from datetime import datetime
from io import BytesIO
import streamlit as st
from PIL import Image
import pandas as pd
import folium
import json


def render_satellite_tab(latest_sat, minio_client, img_bucket="satellite-imgs"):
    """Render the satellite environmental data tab"""
    st.header("🛰️ Satellite Environmental Data")

    if latest_sat:
        wildfire_analysis = latest_sat.get('wildfire_analysis', {})
        detection_summary = wildfire_analysis.get('detection_summary', {})
        fire_indicators = wildfire_analysis.get('fire_indicators', {})
        spectral_analysis = wildfire_analysis.get('spectral_analysis', {})
        environmental_assessment = wildfire_analysis.get('environmental_assessment', {})
        severity_assessment = wildfire_analysis.get('severity_assessment', {})
        spatial_distribution = wildfire_analysis.get('spatial_distribution', {})
        microarea_info = latest_sat.get('microarea_info', {})

        col = st.columns((1.5, 4.5, 2), gap='medium')

        
        with col[0]:
            # ==================== EVENT METADATA ====================  
            # DataFrame 1: Event Metadata
            df_event_metadata = pd.DataFrame({
                'Metric': [
                    'Event Ts',
                    'Area ID',
                    'Risk Level'
                ],
                'Value': [
                    latest_sat.get('event_timestamp', 'N/A')[:19].replace('T', ' '),
                    f"{latest_sat.get('microarea_id', 'N/A')}",
                    severity_assessment.get('risk_level', 'unknown').upper()
                ]
            })

            # ==================== GEOGRAPHIC INFORMATION ====================            
            # DataFrame 2: Geographic Information
            df_geographic_info = pd.DataFrame({
                'Geographic Metric': [
                    'Min Latitude',
                    'Max Latitude', 
                    'Min Longitude',
                    'Max Longitude'
                ],
                'Coordinate': [
                    f"{microarea_info.get('min_lat', 0):.6f}",
                    f"{microarea_info.get('max_lat', 0):.6f}",
                    f"{microarea_info.get('min_long', 0):.6f}",
                    f"{microarea_info.get('max_long', 0):.6f}"
                ]
            })
            
            # ==================== FIRE INDICATORS ====================            
            # DataFrame 3: Fire Indicators
            df_fire_indicators = pd.DataFrame({
                'Fire Indicator': [
                    'High Temp Signatures',
                    'Vegetation Stress',
                    'Moisture Deficit',
                    'Burn Scars',
                    'Smoke Signatures'
                ],
                'Count': [
                    fire_indicators.get('high_temperature_signatures', 0),
                    fire_indicators.get('vegetation_stress_detected', 0),
                    fire_indicators.get('moisture_deficit_areas', 0),
                    fire_indicators.get('burn_scar_indicators', 0),
                    fire_indicators.get('smoke_signatures', 0)
                ]
            })

            # ==================== ENVIROMENTAL ASSESSMENT ====================
            # DataFrame 4: Environmental Assessment
            environmental_data = []

            # Vegetation Health
            veg_health = environmental_assessment.get('vegetation_health', {})
            environmental_data.extend([
                ['Vegetation Status', veg_health.get('status', 'unknown').upper()],
                ['Average NDVI', f"{veg_health.get('average_ndvi', 0):.3f}"],
                ['Healthy Vegetation %', f"{veg_health.get('healthy_vegetation_percent', 0)}%"]
            ])

            # Moisture Conditions
            moisture = environmental_assessment.get('moisture_conditions', {})
            environmental_data.extend([
                ['Moisture Status', moisture.get('status', 'unknown').upper()],
                ['Average NDMI', f"{moisture.get('average_ndmi', 0):.3f}"],
                ['Average NDWI', f"{moisture.get('average_ndwi', 0):.3f}"],
                ['Dry Pixel %', f"{moisture.get('dry_pixel_percent', 0)}%"]
            ])

            # Fire Weather Indicators
            fire_weather = environmental_assessment.get('fire_weather_indicators', {})
            environmental_data.extend([
                ['Fire Weather Level', fire_weather.get('fire_weather_level', 'unknown').upper()],
                ['Temperature Signature %', f"{fire_weather.get('temperature_signature_percent', 0)}%"],
                ['Moisture Deficit %', f"{fire_weather.get('moisture_deficit_percent', 0)}%"],
                ['Smoke Detection %', f"{fire_weather.get('smoke_detection_percent', 0)}%"]
            ])

            # Environmental Stress Level
            env_stress = environmental_assessment.get('environmental_stress_level', 'unknown')
            environmental_data.append(['Environmental Stress', env_stress.upper()])

            df_environmental_assessment = pd.DataFrame(environmental_data, columns=['Environmental Metric', 'Value'])
            df_environmental_assessment["Value"] = df_environmental_assessment["Value"].astype(str)

            # ==================== DETECTION SUMMARY ====================
            # Create DataFrame for Detection Summary
            df_detection_summary = pd.DataFrame({
                "Metric": [
                    "Total Pixels",
                    "Anomalous Pixels",
                    "Anomaly %",
                    "Affected Area",
                    "Confidence"
                ],
                "Value": [
                    detection_summary.get('total_pixels', 0),
                    detection_summary.get('anomalous_pixels', 0),
                    f"{detection_summary.get('anomaly_percentage', 0)}%",
                    f"{detection_summary.get('affected_area_km2', 0)} km²",
                    f"{detection_summary.get('confidence_level', 0)}"
                ]
            })
            df_detection_summary["Value"] = df_detection_summary["Value"].astype(str)

            # ==================== DISPLAY TABLES ====================
            # Display 1: Event Metadata
            st.markdown("#### Event Metadata")
            st.dataframe(
                df_event_metadata,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Metric": st.column_config.TextColumn("Metric", width="medium"),
                    "Value": st.column_config.TextColumn("Value", width="small")
                }
            )
            # Display 2: Detection Summary as DataFrame
            st.markdown("#### Detection Summary")
            st.dataframe(
                df_detection_summary,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Metric": st.column_config.TextColumn("Metric", width="medium"),
                    "Value": st.column_config.TextColumn("Value", width="small")
                }
            )              
            # Display 3: Geographic Information
            st.markdown("#### Geographic INFO")
            st.dataframe(
                df_geographic_info,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Geographic Metric": st.column_config.TextColumn("Geographic Metric", width="medium"),
                    "Coordinate": st.column_config.TextColumn("Coordinate", width="small")
                }
            )
            # Display 4: Fire Indicators
            st.markdown("#### Fire Indicators")
            st.dataframe(
                df_fire_indicators,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Fire Indicator": st.column_config.TextColumn("Fire Indicator", width="medium"),
                    "Count": st.column_config.NumberColumn("Count", format="%d", width="small")
                }
            )
            # Display 5: Environmental Assessment
            st.markdown("#### Env. Assessment")
            st.dataframe(
                df_environmental_assessment,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Environmental Metric": st.column_config.TextColumn("Environmental Metric", width="medium"),
                    "Value": st.column_config.TextColumn("Value", width="small")
                }
            )          


        with col[1]:
            # ==================== IMAGE REFERENCE ====================
            st.markdown("#### LAAP ")
            st.write("Latest Available Assesment Picture")
            
            if 'image_pointer' in latest_sat:
                st.divider()
                object_key = latest_sat.get("image_pointer")
                bucket_name = img_bucket

                try:
                    response = minio_client.get_object(Bucket=bucket_name, Key=object_key)
                    image_bytes = response['Body'].read()
                    image = Image.open(BytesIO(image_bytes))
                    st.image(image, caption=object_key)
                except Exception as e:
                    st.error(f"Error retrieving image: {e}")

            # ==================== RECOMMENDATIONS ====================
            recommendations = wildfire_analysis.get('recommendations', [])
            if recommendations:
                st.markdown("#### Emergency Recommendations")
                
                for i, rec in enumerate(recommendations, 1):
                    if i <= 3:  
                        st.error(f"**{i}.** {rec}")
                    else:  
                        st.warning(f"**{i}.** {rec}")
        
        
        with col[2]:
            # ==================== SEVERITY ASSESSMENT ====================
            st.markdown("#### Severity Assessment")
            
            st.metric("Severity Score", f"{severity_assessment.get('severity_score', 0):.2f}")
            
            # Extract threat classification info
            threat_class = severity_assessment.get('threat_classification', {})
            threat_level = threat_class.get('level', 'unknown').upper()
            priority = threat_class.get('priority', 'N/A')
            evacuation = str(threat_class.get('evacuation_consideration', False))

            # Optional: Display colored alert based on threat level
            if threat_level == 'CRITICAL':
                st.error(f"🚨 Threat: {threat_level}")
            elif threat_level == 'HIGH':
                st.warning(f"⚠️ Threat: {threat_level}")
            else:
                st.info(f"📊 Threat: {threat_level}")

            # Create DataFrame for Threat Classification
            df_threat_classification = pd.DataFrame({
                "Metric": [
                    "Threat Level",
                    "Priority",
                    "Evacuation Needed"
                ],
                "Value": [
                    threat_level,
                    priority,
                    evacuation
                ]
            })

            # Display Threat Classification as DataFrame
            st.markdown("#### 🔐 Threat Classification")
            st.dataframe(
                df_threat_classification,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Metric": st.column_config.TextColumn("Metric", width="medium"),
                    "Value": st.column_config.TextColumn("Value", width="small")
                }
            )
            
            # ==================== SPATIAL DISTRIBUTION ====================
            # Create DataFrame for Spatial Distribution
            df_spatial_distribution = pd.DataFrame({
                "Metric": [
                    "Cluster Density",
                    "Geographic Spread",
                    "Hotspot Concentration %"
                ],
                "Value": [
                    f"{spatial_distribution.get('cluster_density', 0):.4f}",
                    f"{spatial_distribution.get('geographic_spread_km2', 0):.2f} km²",
                    f"{spatial_distribution.get('hotspot_concentration_percent', 0)}%"
                ]
            })
            df_spatial_distribution["Value"] = df_spatial_distribution["Value"].astype(str)

            # Display Spatial Distribution as DataFrame
            st.markdown("#### 📍 Spatial Distribution")
            st.dataframe(
                df_spatial_distribution,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Metric": st.column_config.TextColumn("Metric", width="medium"),
                    "Value": st.column_config.TextColumn("Value", width="small")
                }
            )
            
            # ==================== SPECTRAL ANALYSIS ====================
            # Anomalous Band Averages
            st.write("**Anomalous Band Averages:**")
            anom_bands = spectral_analysis.get('anomalous_band_averages', {})
            df_anom_band_avg = pd.DataFrame({
                'Band': [
                    "B2 (Blue)",
                    "B3 (Green)",
                    "B4 (Red)", 
                    "B8 (NIR)", 
                    "B8A (NIR)",
                    "B11 (SWIR1)",
                    "B12 (SWIR2)"
                ],
                'Value': [
                    f"{anom_bands.get('B2', 0):.3f}",
                    f"{anom_bands.get('B3', 0):.3f}",
                    f"{anom_bands.get('B4', 0):.3f}",
                    f"{anom_bands.get('B8', 0):.3f}",
                    f"{anom_bands.get('B8A', 0):.3f}",
                    f"{anom_bands.get('B11', 0):.3f}",
                    f"{anom_bands.get('B12', 0):.3f}"
                ]
            })

            st.dataframe(
                df_anom_band_avg,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Band": st.column_config.TextColumn(
                        "Band Name",
                        width="medium"
                    ),
                    "Value": st.column_config.TextColumn(
                        "Average Value",
                        width="small"
                    )
                }
            )        
            
            # Scene Band Averages
            st.write("**Scene Band Averages:**")
            scene_bands = spectral_analysis.get('scene_band_averages', {})
            df_scene_band_avg = pd.DataFrame({
                'Band': [
                    "B2 (Blue)",
                    "B3 (Green)",
                    "B4 (Red)", 
                    "B8 (NIR)", 
                    "B8A (NIR)",
                    "B11 (SWIR1)",
                    "B12 (SWIR2)"
                ],
                'Value': [
                    f"{scene_bands.get('B2', 0):.3f}",
                    f"{scene_bands.get('B3', 0):.3f}",
                    f"{scene_bands.get('B4', 0):.3f}",
                    f"{scene_bands.get('B8', 0):.3f}",
                    f"{scene_bands.get('B8A', 0):.3f}",
                    f"{scene_bands.get('B11', 0):.3f}",
                    f"{scene_bands.get('B12', 0):.3f}"
                ]
            })

            st.dataframe(
                df_scene_band_avg,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Band": st.column_config.TextColumn(
                        "Band Name",
                        width="medium"
                    ),
                    "Value": st.column_config.TextColumn(
                        "Average Value",
                        width="small"
                    )
                }
            )
            
            # Anomalous Index Averages
            st.write("**Anomalous Index Averages:**")
            anom_indices = spectral_analysis.get('anomalous_index_averages', {})
            df_anom_indices = pd.DataFrame({
                'Index': [
                    "NDVI",
                    "NDMI",
                    "NDWI",
                    "NBR"
                ],
                'Value': [
                    f"{anom_indices.get('NDVI', 0):.3f}",
                    f"{anom_indices.get('NDMI', 0):.3f}",
                    f"{anom_indices.get('NDWI', 0):.3f}",
                    f"{anom_indices.get('NBR', 0):.3f}"
                ]
            })

            st.dataframe(
                df_anom_indices,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Index": st.column_config.TextColumn(
                        "Index Name",
                        width="medium"
                    ),
                    "Value": st.column_config.TextColumn(
                        "Average Value",
                        width="small"
                    )
                }
            )
        
    else:
        st.info("🔄 Waiting for satellite data...")
        st.write("The system is ready to receive and display real-time satellite environmental data.")


def render_iot_tab(latest_iot, redis_client):
    """Render the IoT environmental sensors tab"""
    st.header("🔧 IoT Environmental Sensors")
    
    if latest_iot:
        # ==================== HEADER MAIN ====================
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.metric(
                "Event ID", 
                latest_iot.get('event_id', 'N/A')
            )
        
        with col2:
            timestamp_ms = latest_iot.get('latest_event_timestamp')
            
            if timestamp_ms is not None:
                try:
                    ts = int(timestamp_ms) / 1000  # convert from ms to s
                    dt = datetime.fromtimestamp(ts)  # create datetime object
                    formatted_ts = dt.strftime('%Y-%m-%d %H:%M:%S')  # readable format
                except Exception:
                    formatted_ts = "Invalid timestamp"
            else:
                formatted_ts = "N/A"

            st.metric("📅 Event Timestamp", formatted_ts)
        
        with col3:
            st.metric(
                "Area ID", 
                f"{latest_iot.get('region_id', 'N/A')}"
            )

        microarea_id = latest_iot.get("region_id")
        redis_key = f"microarea:{microarea_id}"

        if redis_client:
            region_info_json = redis_client.get(redis_key)
            region_info = json.loads(region_info_json)
            min_long = region_info.get("min_long")
            min_lat = region_info.get("min_lat")
            max_long = region_info.get("max_long")
            max_lat = region_info.get("max_lat")
            
            # Compute center & polygon
            center_lat = (min_lat + max_lat) / 2
            center_long = (min_long + max_long) / 2
            polygon_coords = [
                [min_lat, min_long],
                [min_lat, max_long],
                [max_lat, max_long],
                [max_lat, min_long],
                [min_lat, min_long]
            ]     
        
            # Layout: map and sensor data side by side
            col_map, spacer, col_info = st.columns([2, 0.3, 1])

            with col_map:
                # Build map
                m = folium.Map(location=[center_lat, center_long], zoom_start=11)

                folium.Polygon(
                    locations=polygon_coords,
                    color="blue",
                    weight=2,
                    fill=True,
                    fill_color="blue",
                    fill_opacity=0.1,
                    tooltip=f"Microarea: {microarea_id}"
                ).add_to(m)

                # Add station markers
                stations = latest_iot.get("stations", [])
                for station in stations:
                    metadata = station.get("station_metadata", {})
                    position = metadata.get("position", {})

                    lat = position.get("latitude")
                    lon = position.get("longitude")
                    station_id = station.get("station_id", "Unknown ID")

                    # Marker color based on wildfire detection
                    detection = station.get("detection_flags", {})
                    wildfire = detection.get("wildfire_detected", False)
                    color = "red" if wildfire else "blue"

                    folium.Marker(
                        location=[lat, lon],
                        popup=station_id,
                        icon=folium.Icon(color=color, icon="info-sign"),
                    ).add_to(m)

                # Capture click
                map_data = st_folium(m, width=800, height=500, returned_objects=["last_object_clicked"])

            with col_info:
                st.subheader("📊 Sensor Measurements")
                if map_data and map_data.get("last_object_clicked"):
                    clicked_coords = map_data["last_object_clicked"]
                    clicked_lat = clicked_coords["lat"]
                    clicked_lon = clicked_coords["lng"]
                    for station in stations:
                        pos = station["station_metadata"]["position"]
                        if abs(pos["latitude"] - clicked_lat) < 0.0001 and abs(pos["longitude"] - clicked_lon) < 0.0001:
                            measurements = station.get("measurements")
                            if measurements:
                                for k, v in measurements.items():
                                    st.markdown(
                                        f"""
                                        <div style='margin-bottom: 10px; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; background-color: #f4f4f4'>
                                            <div style='font-weight: 600; font-size: 15px;'>{k.replace('_', ' ').title()}</div>
                                            <div style='font-size: 16px; margin-top: 2px;'>{v}</div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                            else:
                                st.write("No anomalies detected")
                            break
                else:
                    st.write("Click a sensor marker to view its data.")
        else:
            print(f" Redis client not initiliazed")

        # === AGGREGATE DATA ===
        st.divider()
        st.subheader("📊 Aggregated Detection Data")
        
        # Extract aggregated data
        aggregated = latest_iot.get("aggregated_detection", {})
        environmental = latest_iot.get("environmental_context", {})
        system_response = latest_iot.get("system_response", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            wildfire_detected = aggregated.get("wildfire_detected", False)
            st.metric(
                "🔥 Wildfire Detection", 
                "DETECTED" if wildfire_detected else "CLEAR",
                delta=f"{aggregated.get('detection_confidence', 0):.1%} confidence"
            )
        
        with col2:
            severity = aggregated.get("severity_score", 0)
            st.metric(
                "⚠️ Severity Score", 
                f"{severity:.2f}",
                delta="High Risk" if severity > 0.7 else "Moderate" if severity > 0.4 else "Low"
            )
        
        with col3:
            aqi = aggregated.get("air_quality_index", 0)
            aqi_status = aggregated.get("air_quality_status", "Unknown")
            st.metric(
                "🌬️ Air Quality Index", 
                f"{aqi:.1f}",
                delta=aqi_status
            )
        
        with col4:
            alert_level = system_response.get("alert_level", "unknown")
            st.metric(
                "🚨 Alert Level", 
                alert_level.replace("_", " ").title(),
                delta="ACTIVE" if system_response.get("event_triggered") else "INACTIVE"
            )

        # === ENVIRONMENTAL CONDITIONS ===
        st.divider()
        st.subheader("🌤️ Environmental Conditions")
        
        weather = environmental.get("weather_conditions", {})
        terrain = environmental.get("terrain_info", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Weather Conditions:**")
            st.write(f"🌡️ Temperature: {weather.get('temperature', 'N/A')}°C")
            st.write(f"💧 Humidity: {weather.get('humidity', 'N/A')}%")
            st.write(f"💨 Wind Speed: {weather.get('wind_speed', 'N/A')} km/h")
            st.write(f"🧭 Wind Direction: {weather.get('wind_direction', 'N/A')}°")
            st.write(f"🌧️ Precipitation Chance: {weather.get('precipitation_chance', 0)*100:.1f}%")
        
        with col2:
            st.write("**Terrain Information:**")
            st.write(f"🌿 Vegetation: {terrain.get('vegetation_type', 'N/A').title()}")
            st.write(f"🌲 Density: {terrain.get('vegetation_density', 'N/A').title()}")
            st.write(f"⛰️ Slope: {terrain.get('slope', 'N/A').title()}")
            st.write(f"🧭 Aspect: {terrain.get('aspect', 'N/A').title()}")

        # === FIRE BEHAVIOUR ===
        if "fire_behavior" in aggregated and wildfire_detected:
            st.divider()
            st.subheader("🔥 Fire Behavior Analysis")
            
            fire_behavior = aggregated["fire_behavior"]
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Spread Rate", 
                    fire_behavior.get("spread_rate", "Unknown").title()
                )
            
            with col2:
                st.metric(
                    "Direction", 
                    fire_behavior.get("direction", "Unknown").title()
                )
            
            with col3:
                st.metric(
                    "Speed", 
                    f"{fire_behavior.get('estimated_speed_mph', 0)} mph"
                )
            
            ignition_time = aggregated.get("estimated_ignition_time")
            if ignition_time:
                st.info(f"🕐 Estimated Ignition Time: {ignition_time}")

        # === SYSTEM RESPONSE ===
        st.divider()
        st.subheader("🚨 System Response")
        
        at_risk = system_response.get("at_risk_assets", {})
        
        if "population_centers" in at_risk:
            st.write("**Population Centers at Risk:**")
            for center in at_risk["population_centers"]:
                st.warning(f"🏘️ {center.get('name')}: {center.get('population')} people at {center.get('distance_meters')}m distance (Priority: {center.get('evacuation_priority')})")
        
        if "critical_infrastructure" in at_risk:
            st.write("**Critical Infrastructure at Risk:**")
            for infra in at_risk["critical_infrastructure"]:
                st.error(f"🏭 {infra.get('name')} ({infra.get('type')}): {infra.get('distance_meters')}m distance (Priority: {infra.get('priority')})")

        if "recommended_actions" in system_response:
            st.write("**Recommended Actions:**")
            for action in system_response["recommended_actions"]:
                priority_color = "🔴" if action.get('priority') == 'high' else "🟡" if action.get('priority') == 'medium' else "🟢"
                st.write(f"{priority_color} {action.get('action', '').replace('_', ' ').title()} (Priority: {action.get('priority', 'N/A')})")
                
                if 'recommended_resources' in action:
                    resources = ", ".join([r.replace('_', ' ').title() for r in action['recommended_resources']])
                    st.write(f"   Resources: {resources}")
                
                if 'radius_meters' in action:
                    st.write(f"   Radius: {action['radius_meters']}m")
                if 'evacuation_direction' in action:
                    st.write(f"   Direction: {action['evacuation_direction']}")

        if "sent_notifications_to" in system_response:
            st.write("**Notifications Sent:**")
            for notification in system_response["sent_notifications_to"]:
                status_icon = "✅" if notification.get('delivery_status') == 'confirmed' else "❌"
                st.write(f"{status_icon} {notification.get('agency', '').replace('_', ' ').title()} - {notification.get('delivery_status')} at {notification.get('notification_timestamp')}")

        # === TECHNICAL REPORT ===
        with st.expander("🔧 Technical Information"):
            st.write(f"**Event ID:** {latest_iot.get('event_id')}")
            st.write(f"**Region ID:** {latest_iot.get('region_id')}")
            st.write(f"**Event Type:** {latest_iot.get('event_type', '').title()}")
            st.write(f"**Detection Source:** {latest_iot.get('detection_source', '').replace('_', ' ').title()}")
            st.write(f"**Response Timestamp:** {latest_iot.get('response_timestamp')}")
            st.write(f"**Latest Event Timestamp:** {latest_iot.get('latest_event_timestamp')}")
            
            if aggregated.get("anomaly_detected"):
                st.write(f"**Anomaly Type:** {aggregated.get('anomaly_type', '').title()}")

    else:
        st.info("🔄 Waiting for IoT data...")
        st.write("The system is ready to receive and display real-time IoT environmental data.")


def render_social_tab(latests_msg):
    st.subheader("📥 Latest Classified Social Media Messages")
    # ==================== RECENT MESSAGES DISPLAY ====================
    if latests_msg:
        # Display last 10 messages in reverse order
        for msg in reversed(latests_msg[-10:]):
            timestamp = msg.get("timestamp", "N/A")
            area_id = msg.get("microarea_id", "N/A")
            category = msg.get("category", "N/A")
            content = msg.get("message", "No content")

            with st.container():
                st.markdown(f"""
                    <div style="background-color:#1e1e1e; padding:10px; border-radius:8px; margin-bottom:10px;">
                        <div style="color:#aaa; font-size:13px;">
                            📍 <b>{area_id}</b> &nbsp;&nbsp; 🕒 {timestamp} &nbsp;&nbsp;
                            🧭 <b>{category.replace("_", " ").title()}</b>
                        </div>
                        <div style="margin-top:5px; color:#fff;">💬 {content}</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Waiting for social media messages...")

    # ==================== INTERACTIVE MAP ====================
    st.divider()
    st.subheader("🗺️ Interactive Map of Message Locations")

    # Initialize session state for map
    if "map_active" not in st.session_state:
        st.session_state.map_active = False
    if "map_points" not in st.session_state:
        st.session_state.map_points = []
    if "map_reset_timestamp" not in st.session_state:
        st.session_state.map_reset_timestamp = datetime.min
    if "processed_message_ids" not in st.session_state:
        st.session_state.processed_message_ids = set()

    # Buttons to update or reset map
    col_update, col_reset, _ = st.columns([2, 2, 6])
    with col_update:
        update_clicked = st.button("🟢 Update Map", key="update_map_btn", use_container_width=True)
    with col_reset:
        reset_clicked = st.button("🔴 Reset Map", key="reset_map_btn", use_container_width=True)

    # If update clicked, add new messages with geo-coordinates
    if update_clicked and latests_msg:
        new_points = []
        for i, msg in enumerate(latests_msg):
            # Create unique ID for each message
            msg_id = f"{msg.get('timestamp', '')}_{i}_{msg.get('microarea_id', '')}"
            
            # Skip if already processed
            if msg_id in st.session_state.processed_message_ids:
                continue
                
            # Check if message has coordinates
            lat = msg.get("latitude")
            lon = msg.get("longitude")
            
            if lat is not None and lon is not None:
                try:
                    # Validate coordinates
                    lat_float = float(lat)
                    lon_float = float(lon)
                    
                    # Basic validation for reasonable coordinates
                    if -90 <= lat_float <= 90 and -180 <= lon_float <= 180:
                        # Check timestamp if available
                        try:
                            if msg.get("timestamp"):
                                msg_ts = datetime.strptime(msg["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
                                if msg_ts > st.session_state.map_reset_timestamp:
                                    new_points.append(msg)
                                    st.session_state.processed_message_ids.add(msg_id)
                            else:
                                # If no timestamp, add anyway
                                new_points.append(msg)
                                st.session_state.processed_message_ids.add(msg_id)
                        except (ValueError, TypeError):
                            # If timestamp parsing fails, still add the message
                            new_points.append(msg)
                            st.session_state.processed_message_ids.add(msg_id)
                except (ValueError, TypeError):
                    # Skip messages with invalid coordinates
                    continue
        
        if new_points:
            st.session_state.map_points.extend(new_points)
            st.session_state.map_active = True
            st.success(f"Added {len(new_points)} new messages to map!")
        else:
            st.info("No new messages with valid coordinates found.")

    # If reset clicked, clear the map
    if reset_clicked:
        st.session_state.map_points = []
        st.session_state.map_active = False
        st.session_state.map_reset_timestamp = datetime.utcnow()
        st.session_state.processed_message_ids = set()
        st.success("Map reset successfully!")

    # ======== CATEGORY FILTER FOR MAP ========
    pretty_labels = {
        "emergency_help_request": "Emergency Help Request",
        "infrastructure_or_property_damage": "Infrastructure or Property Damage",
        "emotional_reaction_to_wildfire": "Emotional Reaction to Wildfire",
        "official_emergency_announcement": "Official Emergency Announcement"
    }
    label_to_category = {v: k for k, v in pretty_labels.items()}

    # Fix the accessibility warning by providing a proper label
    st.markdown("**Select message category to show on map:**")
    selected_label = st.selectbox(
        "Category Filter", 
        options=list(pretty_labels.values()), 
        key="category_selector",
        label_visibility="collapsed"
    )
    
    selected_category = label_to_category[selected_label]

    # Icon and color for each category
    icon_map = {
        "emergency_help_request": ("exclamation-triangle", "red"),
        "infrastructure_or_property_damage": ("tools", "orange"),
        "emotional_reaction_to_wildfire": ("comment", "blue"),
        "official_emergency_announcement": ("bullhorn", "green"),
    }

    # Create map centered on California
    m = folium.Map(location=[36.7783, -119.4179], zoom_start=6)

    # Track if we have any markers to display
    markers_added = 0
    marker_locations = []

    if st.session_state.map_active and st.session_state.map_points:
        # Filter messages by selected category
        filtered_messages = [msg for msg in st.session_state.map_points 
                           if msg.get("category") == selected_category]
        
        if filtered_messages:
            # Create marker cluster for better performance
            cluster = MarkerCluster().add_to(m)
            
            for msg in filtered_messages:
                try:
                    lat = float(msg["latitude"])
                    lon = float(msg["longitude"])
                    content = msg.get("message", "No content")
                    timestamp = msg.get("timestamp", "N/A")
                    area_id = msg.get("microarea_id", "N/A")
                    
                    # Truncate long messages for popup
                    if len(content) > 200:
                        content = content[:200] + "..."
                    
                    icon_name, color = icon_map.get(selected_category, ("info-sign", "gray"))
                    
                    # Create popup content
                    popup_content = f"""
                    <div style="width: 300px;">
                        <b>Area:</b> {area_id}<br>
                        <b>Time:</b> {timestamp}<br>
                        <b>Category:</b> {selected_label}<br>
                        <hr>
                        <b>Message:</b><br>
                        {content}
                    </div>
                    """

                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_content, max_width=350),
                        icon=folium.Icon(color=color, icon=icon_name, prefix="fa")
                    ).add_to(cluster)
                    
                    markers_added += 1
                    marker_locations.append([lat, lon])
                    
                except (ValueError, TypeError, KeyError) as e:
                    # Skip invalid markers
                    continue

            # Adjust map view to fit all markers if we have any
            if marker_locations:
                try:
                    m.fit_bounds(marker_locations)
                except Exception:
                    # If fit_bounds fails, keep default view
                    pass

    # Display map with current status
    col_map, col_status = st.columns([3, 1])
    
    with col_map:
        st_folium(m, use_container_width=True, height=600)
    
    with col_status:
        st.markdown("### Map Status")
        st.metric("Total Messages", len(st.session_state.map_points))
        st.metric(f"{selected_label}", markers_added)
        
        if st.session_state.map_points:
            # Show available categories in current data
            categories_in_data = set(msg.get("category") for msg in st.session_state.map_points)
            st.markdown("**Available Categories:**")
            for cat in categories_in_data:
                if cat in pretty_labels:
                    count = sum(1 for msg in st.session_state.map_points if msg.get("category") == cat)
                    st.write(f"• {pretty_labels[cat]}: {count}")

    # ==================== CATEGORY COUNT SECTION ====================
    st.divider()
    st.subheader("📊 Message Count by Category")

    all_categories = list(pretty_labels.keys())

    # Initialize session state
    if "category_counts" not in st.session_state:
        st.session_state.category_counts = {cat: 0 for cat in all_categories}
    if "category_reset_timestamp" not in st.session_state:
        st.session_state.category_reset_timestamp = datetime.min
    if "category_last_update" not in st.session_state:
        st.session_state.category_last_update = None
    if "category_history" not in st.session_state:
        st.session_state.category_history = {cat: [] for cat in all_categories}
    if "processed_count_message_ids" not in st.session_state:
        st.session_state.processed_count_message_ids = set()

    # Update / Reset buttons
    col_up, col_reset, _ = st.columns([2, 2, 6])
    with col_up:
        update_cat = st.button("🟢 Update Count", key="update_cat_btn", use_container_width=True)
    with col_reset:
        reset_cat = st.button("🔴 Reset Count", key="reset_cat_btn", use_container_width=True)

    if update_cat and latests_msg:
        # Store previous counts for delta calculation
        previous_counts = st.session_state.category_counts.copy()
        
        # Update counters for new messages
        new_messages_count = 0
        for i, msg in enumerate(latests_msg):
            # Create unique ID for each message
            msg_id = f"{msg.get('timestamp', '')}_{i}_{msg.get('microarea_id', '')}"
            
            # Skip if already processed for counting
            if msg_id in st.session_state.processed_count_message_ids:
                continue
                
            cat = msg.get("category")
            if cat in st.session_state.category_counts:
                try:
                    # Check if message is after reset timestamp
                    if msg.get("timestamp"):
                        ts = datetime.strptime(msg["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
                        if ts > st.session_state.category_reset_timestamp:
                            st.session_state.category_counts[cat] += 1
                            st.session_state.processed_count_message_ids.add(msg_id)
                            new_messages_count += 1
                    else:
                        # If no timestamp, count anyway
                        st.session_state.category_counts[cat] += 1
                        st.session_state.processed_count_message_ids.add(msg_id)
                        new_messages_count += 1
                except (ValueError, TypeError):
                    # If timestamp parsing fails, still count the message
                    st.session_state.category_counts[cat] += 1
                    st.session_state.processed_count_message_ids.add(msg_id)
                    new_messages_count += 1

        st.session_state.category_last_update = datetime.utcnow()
        
        if new_messages_count > 0:
            st.success(f"Processed {new_messages_count} new messages!")
        else:
            st.info("No new messages to count.")

        # Update history for delta calculation
        for cat in all_categories:
            if len(st.session_state.category_history[cat]) == 0:
                st.session_state.category_history[cat].append(previous_counts[cat])
            st.session_state.category_history[cat].append(st.session_state.category_counts[cat])
            # Keep only last 2 history points
            if len(st.session_state.category_history[cat]) > 2:
                st.session_state.category_history[cat] = st.session_state.category_history[cat][-2:]

    if reset_cat:
        st.session_state.category_counts = {cat: 0 for cat in all_categories}
        st.session_state.category_reset_timestamp = datetime.utcnow()
        st.session_state.category_last_update = None
        st.session_state.category_history = {cat: [] for cat in all_categories}
        st.session_state.processed_count_message_ids = set()
        st.success("Category counts reset successfully!")

    # Show last update timestamp
    if st.session_state.category_last_update:
        formatted_time = st.session_state.category_last_update.strftime("%d %b %Y - %H:%M:%S (UTC)")
        st.caption(f"🕒 Last update: {formatted_time}")
    else:
        st.caption("🕒 Last update: —")

    # Show metric boxes for each category
    cols = st.columns(len(all_categories))
    for idx, cat in enumerate(all_categories):
        count = st.session_state.category_counts[cat]
        history = st.session_state.category_history[cat]

        if len(history) < 2:
            delta = None
        else:
            diff = history[-1] - history[-2]
            delta = f"+{diff}" if diff > 0 else str(diff) if diff != 0 else None

        with cols[idx]:
            st.metric(
                label=pretty_labels[cat],
                value=f"{count}",
                delta=delta
            )


def render_sidebar_status(social_messages, iot_data, sat_data, social_count=0, iot_count=0, sat_count=0):
    """Render the system status sidebar"""
    st.sidebar.header("🖥️ System Status")
    st.sidebar.write(f"📱 Social Messages: {len(social_messages)}")
    st.sidebar.write(f"🔧 IoT Readings: {len(iot_data)}")
    st.sidebar.write(f"🛰️ Satellite Data: {len(sat_data)}")
    st.sidebar.write(f"⏱️ Last Update: {datetime.now().strftime('%H:%M:%S')}")
    
    # Show processing stats
    if social_count > 0 or iot_count > 0 or sat_count > 0:
        st.sidebar.write("📊 Last Batch:")
        st.sidebar.write(f"  Social: {social_count}")
        st.sidebar.write(f"  IoT: {iot_count}")
        st.sidebar.write(f"  Satellite: {sat_count}")

    # System health indicator
    if social_messages or iot_data or sat_data:
        st.sidebar.success("🟢 System Operational")
    else:
        st.sidebar.warning("🟡 Waiting for Data Streams")
    
    # Control buttons
    if st.sidebar.button("🔄 Force Refresh"):
        st.rerun()

    if st.sidebar.button("🗑️ Clear All Data"):
        st.session_state.social_messages = []
        st.session_state.iot_data = []
        st.session_state.sat_data = []
        st.rerun()

        