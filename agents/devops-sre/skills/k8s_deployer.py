"""
Kubernetes Deployer Skill — Generate production-ready Kubernetes manifests.

Creates complete K8s deployment configurations including Deployment, Service, Ingress,
ConfigMap, Secret template, HPA, and PDB. Follows security best practices (non-root,
read-only filesystem, resource limits, network policies).

Part of the DevOps SRE agent in the HermesHub marketplace.
"""
import json
from typing import Any


SCHEMA = {
    "name": "devops_k8s_deployer",
    "description": (
        "Generate production-ready Kubernetes manifests for deploying applications. "
        "Creates Deployment, Service, Ingress, ConfigMap, Secret template, "
        "HorizontalPodAutoscaler, and PodDisruptionBudget. Includes security hardening "
        "(non-root, readOnlyRootFilesystem, resource limits) and health checks. "
        "Use when: deploying to Kubernetes, generating K8s manifests, or reviewing deployment configs."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Application name (lowercase, used for labels and resource names)."
            },
            "namespace": {
                "type": "string",
                "description": "Kubernetes namespace.",
                "default": "default"
            },
            "image": {
                "type": "string",
                "description": "Container image (e.g., 'ghcr.io/org/app:v1.0.0').",
                "default": "nginx:1.25"
            },
            "port": {
                "type": "integer",
                "description": "Container port.",
                "default": 8000
            },
            "replicas": {
                "type": "integer",
                "description": "Number of replicas.",
                "default": 2
            },
            "resources": {
                "type": "object",
                "description": "Custom resource limits/requests: {cpu_request, cpu_limit, memory_request, memory_limit}.",
                "default": {}
            },
            "domain": {
                "type": "string",
                "description": "Domain name for Ingress (e.g., 'api.example.com'). Leave empty to skip Ingress.",
                "default": ""
            },
            "include_hpa": {
                "type": "boolean",
                "description": "Whether to include a HorizontalPodAutoscaler.",
                "default": True
            },
            "include_pdb": {
                "type": "boolean",
                "description": "Whether to include a PodDisruptionBudget.",
                "default": True
            }
        },
        "required": ["app_name"]
    }
}


def handler(args: dict[str, Any]) -> str:
    """Generate Kubernetes manifests."""
    try:
        app_name = args.get("app_name", "").strip().lower()
        namespace = args.get("namespace", "default")
        image = args.get("image", "nginx:1.25")
        port = args.get("port", 8000)
        replicas = args.get("replicas", 2)
        resources = args.get("resources", {})
        domain = args.get("domain", "")
        include_hpa = args.get("include_hpa", True)
        include_pdb = args.get("include_pdb", True)

        # Validate app name
        if not app_name:
            return json.dumps({"error": "app_name is required and cannot be empty."})
        if not app_name.replace("-", "").replace("_", "").isalnum():
            return json.dumps({"error": f"Invalid app_name '{app_name}'. Use lowercase letters, digits, hyphens, and underscores only."})

        # Resource defaults
        cpu_request = resources.get("cpu_request", "100m")
        cpu_limit = resources.get("cpu_limit", "500m")
        memory_request = resources.get("memory_request", "128Mi")
        memory_limit = resources.get("memory_limit", "512Mi")

        manifests: dict[str, str] = {}

        # 1. Namespace (if not default)
        if namespace != "default":
            manifests["00-namespace.yaml"] = _namespace(namespace)

        # 2. ConfigMap
        manifests["01-configmap.yaml"] = _configmap(app_name, namespace)

        # 3. Secret template
        manifests["02-secret.yaml"] = _secret_template(app_name, namespace)

        # 4. Deployment
        manifests["03-deployment.yaml"] = _deployment(
            app_name, namespace, image, port, replicas,
            cpu_request, cpu_limit, memory_request, memory_limit
        )

        # 5. Service
        manifests["04-service.yaml"] = _service(app_name, namespace, port)

        # 6. Ingress (if domain provided)
        if domain:
            manifests["05-ingress.yaml"] = _ingress(app_name, namespace, domain, port)

        # 7. HPA
        if include_hpa:
            manifests["06-hpa.yaml"] = _hpa(app_name, namespace)

        # 8. PDB
        if include_pdb:
            manifests["07-pdb.yaml"] = _pdb(app_name, namespace)

        # 9. NetworkPolicy
        manifests["08-networkpolicy.yaml"] = _networkpolicy(app_name, namespace, port)

        return json.dumps({
            "success": True,
            "app_name": app_name,
            "namespace": namespace,
            "manifests": manifests,
            "deploy_order": list(manifests.keys()),
            "instructions": {
                "apply": f"kubectl apply -f k8s/ --namespace={namespace}",
                "verify": f"kubectl rollout status deployment/{app_name} -n {namespace}",
                "logs": f"kubectl logs -f deployment/{app_name} -n {namespace}",
                "rollback": f"kubectl rollout undo deployment/{app_name} -n {namespace}"
            }
        })

    except Exception as e:
        return json.dumps({"error": f"K8s manifest generation failed: {str(e)}", "type": type(e).__name__})


def _namespace(ns: str) -> str:
    return f'''apiVersion: v1
kind: Namespace
metadata:
  name: {ns}
  labels:
    name: {ns}
    environment: production'''


def _configmap(app: str, ns: str) -> str:
    return f'''apiVersion: v1
kind: ConfigMap
metadata:
  name: {app}-config
  namespace: {ns}
  labels:
    app: {app}
data:
  # Non-sensitive configuration
  LOG_LEVEL: "info"
  ENVIRONMENT: "production"
  # Add your config keys here'''


def _secret_template(app: str, ns: str) -> str:
    return f'''# WARNING: Do NOT commit real secret values!
# Use external secret management (Vault, Sealed Secrets, cloud KMS).
# This is a template — inject values at deploy time.
apiVersion: v1
kind: Secret
metadata:
  name: {app}-secret
  namespace: {ns}
  labels:
    app: {app}
type: Opaque
stringData:
  # Replace with actual values via kubectl, sealed-secrets, or external-secrets
  DATABASE_URL: "postgresql://user:password@host:5432/db"
  API_KEY: "replace-me"
  # Add your secret keys here'''


def _deployment(
    app: str, ns: str, image: str, port: int, replicas: int,
    cpu_req: str, cpu_lim: str, mem_req: str, mem_lim: str
) -> str:
    return f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app}
  namespace: {ns}
  labels:
    app: {app}
    version: v1
spec:
  replicas: {replicas}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: {app}
  template:
    metadata:
      labels:
        app: {app}
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "{port}"
        prometheus.io/path: "/metrics"
    spec:
      terminationGracePeriodSeconds: 30
      serviceAccountName: {app}-sa
      securityContext:
        fsGroup: 1000
        runAsNonRoot: true
      containers:
        - name: {app}
          image: {image}
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: {port}
              protocol: TCP
          envFrom:
            - configMapRef:
                name: {app}-config
            - secretRef:
                name: {app}-secret
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
          resources:
            requests:
              cpu: {cpu_req}
              memory: {mem_req}
            limits:
              cpu: {cpu_lim}
              memory: {mem_lim}
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 15
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            runAsGroup: 1000
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir:
            sizeLimit: 100Mi'''


def _service(app: str, ns: str, port: int) -> str:
    return f'''apiVersion: v1
kind: Service
metadata:
  name: {app}
  namespace: {ns}
  labels:
    app: {app}
spec:
  type: ClusterIP
  selector:
    app: {app}
  ports:
    - name: http
      port: 80
      targetPort: {port}
      protocol: TCP'''


def _ingress(app: str, ns: str, domain: str, port: int) -> str:
    return f'''apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {app}
  namespace: {ns}
  labels:
    app: {app}
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - {domain}
      secretName: {app}-tls
  rules:
    - host: {domain}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {app}
                port:
                  name: http'''


def _hpa(app: str, ns: str) -> str:
    return f'''apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {app}
  namespace: {ns}
  labels:
    app: {app}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {app}
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30'''


def _pdb(app: str, ns: str) -> str:
    return f'''apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {app}
  namespace: {ns}
  labels:
    app: {app}
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: {app}'''


def _networkpolicy(app: str, ns: str, port: int) -> str:
    return f'''apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {app}
  namespace: {ns}
  labels:
    app: {app}
spec:
  podSelector:
    matchLabels:
      app: {app}
  policyTypes:
    - Ingress
  ingress:
    # Allow from the same namespace
    - from:
        - podSelector: {{}}
      ports:
        - port: {port}
          protocol: TCP
    # Allow from ingress controller namespace
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-nginx
      ports:
        - port: {port}
          protocol: TCP
    # Allow from monitoring (Prometheus)
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: monitoring
      ports:
        - port: {port}
          protocol: TCP'''
